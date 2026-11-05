"""`scripts/s3c_ann_net_october_1455.py` (#1455; H5, registration groundwork: the known-limits list, development tier): (s3c-ann-net) with the 15 October
`tax_date` label at the target day.

Written first, against `metadata/s3c_ann_net_october_1455.json`. The study changes one thing in the model: the `tax_date` entry of the term table, which is the
published flag OR-ed with `tax_date_october.october_window`. The arithmetic of that change and its guard are pinned here on hand cases; the walks are #1288's.

**Recorded mutations** (4 November 2026).

1. In `require_only_october` (the arm's table may differ from the published one only by adding October-window days to the `tax_date` flag), the line

       if arm_flag != published_flag and not (arm_flag == 1 and not published_flag and october):

   was changed to `if False:`. `OnlyOctoberTests.test_a_flag_added_outside_october_is_refused` then failed with `AssertionError: ValueError not raised`;
   restored, it passes.

2. In `require_instant` (the study is made at 18:00), the line `if decision_time != INSTANT_TIME:` was changed to `if False:`.
   `InstantTests.test_a_run_at_another_instant_is_refused` then failed with `AssertionError: ValueError not raised`; restored, it passes.
"""

from __future__ import annotations

import importlib.util
import sys
import unittest
from datetime import date, time, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
_spec = importlib.util.spec_from_file_location("s3c_ann_net_october_1455", ROOT / "scripts" / "s3c_ann_net_october_1455.py")
script = importlib.util.module_from_spec(_spec)
sys.modules["s3c_ann_net_october_1455"] = script
_spec.loader.exec_module(script)

from repo_model import spread_mr_calendar as cal, tax_date_october  # noqa: E402
from repo_model.data import DailyObservation  # noqa: E402


def business_days(first, n):
    day, out = first, []
    while len(out) < n:
        if day.weekday() < 5:
            out.append(day)
        day += timedelta(days=1)
    return out


# 2025: 15 October is a Wednesday; the window is 15, 16 and 17 October (Columbus Day was 13 October, before the deadline).
DAYS = business_days(date(2025, 10, 6), 20)


def panel(tax=()):
    return [DailyObservation(d, {"tax_date": 1.0 if d in tax else 0.0, "iorb_announced_change_bps": None}) for d in DAYS]


def table(rows):
    return script.OctoberTermTable(rows, [], [], calendar=[], decision_time=time(18, 0))


class LabelTests(unittest.TestCase):
    def test_the_october_window_is_the_deadline_and_two_market_days(self):
        window = [d for d in DAYS if tax_date_october.october_window(d)]
        self.assertEqual(window, [date(2025, 10, 15), date(2025, 10, 16), date(2025, 10, 17)])

    def test_the_arm_flags_the_window_at_every_lead_and_nothing_else(self):
        base = cal.TermTable(panel(), [], calendar=[], decision_time=time(18, 0))
        arm = table(panel())
        for lead in cal.HORIZONS:
            for row, day in enumerate(DAYS):
                expected = 1 if tax_date_october.october_window(day) else 0
                self.assertEqual(arm.flag("tax_date", lead, row), expected, (lead, day))
                self.assertEqual(base.flag("tax_date", lead, row), 0)
                for term in cal.TERMS:
                    if term.name != "tax_date" and not term.name.startswith("settlement"):  # the settlement terms are the announced ones
                        self.assertEqual(arm.flag(term.name, lead, row), base.flag(term.name, lead, row), (term.name, lead, day))

    def test_a_published_flag_is_kept(self):
        earlier = date(2025, 10, 8)
        arm = table(panel(tax=(earlier,)))
        self.assertEqual(arm.flag("tax_date", 1, DAYS.index(earlier)), 1)
        self.assertEqual(arm.flag("tax_date", 1, DAYS.index(date(2025, 10, 15))), 1)

    def test_the_label_is_read_at_the_target_row_not_one_row_off(self):
        arm = table(panel())
        row = DAYS.index(date(2025, 10, 14))
        self.assertEqual(arm.flag("tax_date", 1, row), 0)
        self.assertEqual(arm.flag("tax_date", 1, row + 1), 1)
        self.assertEqual(arm.flag("tax_date", 1, row + 4), 0)


class OnlyOctoberTests(unittest.TestCase):
    PUBLISHED = [0, 0, 1, 0]
    DATES = [date(2025, 9, 15), date(2025, 10, 14), date(2025, 10, 15), date(2025, 10, 20)]

    def test_the_flag_added_in_the_window_passes(self):
        script.require_only_october(self.PUBLISHED, [0, 0, 1, 0], self.DATES)
        script.require_only_october([0, 0, 0, 0], [0, 0, 1, 0], self.DATES)

    def test_a_flag_added_outside_october_is_refused(self):
        with self.assertRaises(ValueError):
            script.require_only_october(self.PUBLISHED, [1, 0, 1, 0], self.DATES)

    def test_a_published_flag_cleared_is_refused(self):
        with self.assertRaises(ValueError):
            script.require_only_october(self.PUBLISHED, [0, 0, 0, 0], self.DATES)

    def test_a_flag_on_an_october_day_outside_the_window_is_refused(self):
        with self.assertRaises(ValueError):
            script.require_only_october(self.PUBLISHED, [0, 1, 1, 0], self.DATES)


class InstantTests(unittest.TestCase):
    def test_a_run_at_another_instant_is_refused(self):
        with self.assertRaises(ValueError):
            script.require_instant(time(16, 0))
        script.require_instant(time(18, 0))


class GroupTests(unittest.TestCase):
    TARGETS = [date(2018, 10, 15), date(2019, 10, 16), date(2019, 11, 1), date(2021, 10, 18), date(2025, 10, 15), date(2026, 3, 2)]

    def test_the_october_groups_split_the_motivating_years_out(self):
        groups = dict(((label), members) for _s, label, _g, members in script.october_groups(self.TARGETS))
        self.assertEqual(groups["all October-window targets"], [date(2018, 10, 15), date(2019, 10, 16), date(2021, 10, 18), date(2025, 10, 15)])
        self.assertEqual(groups["October-window targets, not 2019 or 2025"], [date(2018, 10, 15), date(2021, 10, 18)])
        self.assertEqual(groups["October-window targets of 2019 and 2025 (the days that prompted the label)"], [date(2019, 10, 16), date(2025, 10, 15)])


class ReadingTests(unittest.TestCase):
    def test_the_reading_follows_the_interval(self):
        self.assertEqual(script.reading({"difference_interval": [0.1, 0.4]}), "gain")
        self.assertEqual(script.reading({"difference_interval": [-0.4, -0.1]}), "cost")
        self.assertEqual(script.reading({"difference_interval": [-0.1, 0.4]}), "undecided")
        self.assertEqual(script.reading({"identical": True}), "identical")
        self.assertEqual(script.reading(None), "not read")


if __name__ == "__main__":
    unittest.main()
