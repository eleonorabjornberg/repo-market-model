"""The narrowed coupon-settlement flag and its declared rule (#339).

`scripts/settlement_flag_candidate.py` scores a candidate that marks only the ruled settlements against the
published declaration (`docs/pivot/settlement-flag-test.md`). The tests pin what the flag marks, that it can never
mark a day the published flag does not, and the rule's gate and cell verdicts.

Recorded mutation for the subset guard (the narrowed flag is public no later than the published flag only if it is
a subset of it): in `NarrowedFoldPid._calendar`, the `if narrowed > published: raise ValueError(...)` was deleted;
`SubsetGuardTest.test_a_day_the_published_flag_does_not_mark_is_refused` then failed with `AssertionError` (no
`ValueError` raised). Restored.
"""

from __future__ import annotations

import importlib.util
import sys
import unittest
from datetime import date, timedelta
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))


def _load():
    spec = importlib.util.spec_from_file_location("flag_candidate_under_test",
                                                  ROOT / "scripts" / "settlement_flag_candidate.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


sfc = _load()


def _record(issue, term, kind="Note", floating="No", tips="No"):
    return {"issue_date": issue, "security_type": kind, "security_term": term, "floating_rate": floating,
            "inflation_index_security": tips}


def _business_days(start, end):
    day, out = start, []
    while day <= end:
        if day.weekday() < 5:
            out.append(day)
        day += timedelta(days=1)
    return out


class NarrowedDaysTest(unittest.TestCase):
    days = _business_days(date(2019, 1, 1), date(2019, 12, 31))

    def flagged(self, *records):
        return sfc.narrowed_days(self.days, list(records))

    def test_the_ruled_settlements_mark_their_days(self):
        # 15 Sep 2019 is a Sunday: the next business day is Monday the 16th.
        got = self.flagged(_record("2019-01-15", "3-Year"), _record("2019-09-16", "10-Year"),
                           _record("2019-01-31", "2-Year"), _record("2019-04-01", "5-Year"),
                           _record("2019-04-30", "7-Year"), _record("2019-02-15", "9-Year 11-Month", "Bond"))
        self.assertEqual(sorted(got), [date(2019, 1, 15), date(2019, 1, 31), date(2019, 2, 15),
                                       date(2019, 4, 1), date(2019, 4, 30), date(2019, 9, 16)])

    def test_other_securities_and_off_date_settlements_do_not(self):
        got = self.flagged(
            _record("2019-01-31", "2-Year", floating="Yes"),          # an FRN on a ruled date
            _record("2019-02-15", "10-Year", tips="Yes"),             # TIPS on a ruled date
            _record("2019-02-15", "20-Year", "Bond"),                 # 20-year on a ruled date
            _record("2019-06-26", "10-Year"),                         # a reopening off the pattern's dates
            _record("2019-03-15", "5-Year"),                          # a month-end kind mid-month
            _record("2019-04-01", "10-Year"),                         # a mid-month kind at month-end
            _record("2019-03-29", "26-Week", "Bill"))
        self.assertEqual(got, {})


class SubsetGuardTest(unittest.TestCase):
    def build(self, narrowed):
        online = sfc.NarrowedFoldPid.__new__(sfc.NarrowedFoldPid)
        online._dates = [date(2019, 1, 15)]
        online._narrowed = narrowed
        return online

    def test_the_last_indicator_is_replaced_by_the_narrowed_flag(self):
        with mock.patch.object(sfc.NestedFoldPid.__mro__[1], "_calendar", return_value=(0, 0, 0, 1)):
            self.assertEqual(self.build({})._calendar(0), (0, 0, 0, 0))
            self.assertEqual(self.build({date(2019, 1, 15): ["3-Year"]})._calendar(0), (0, 0, 0, 1))

    def test_a_day_the_published_flag_does_not_mark_is_refused(self):
        with mock.patch.object(sfc.NestedFoldPid.__mro__[1], "_calendar", return_value=(0, 0, 0, 0)):
            with self.assertRaises(ValueError):
                self.build({date(2019, 1, 15): ["3-Year"]})._calendar(0)


def _paired(mean, lower, upper, cells=None):
    interval = {"lower": lower, "upper": upper}
    regime = {k: {"count": n, "interval": {"lower": a, "upper": b}, "mean": 0.0}
              for k, (n, a, b) in (cells or {"2018-19": (100, -1.0, 1.0)}).items()}
    return {"mean": mean, "interval": interval, "splits": {"by_regime": regime, "by_day_type": {}}}


class RuleTest(unittest.TestCase):
    def test_the_gate_needs_a_positive_mean_and_a_positive_lower_bound(self):
        self.assertTrue(sfc.judge("x", _paired(0.1, 0.01, 0.2))["gate"])
        self.assertFalse(sfc.judge("x", _paired(0.1, -0.01, 0.2))["gate"])
        self.assertFalse(sfc.judge("x", _paired(-0.1, 0.01, 0.2))["gate"])

    def test_a_cell_is_worse_only_when_its_upper_bound_is_below_zero(self):
        got = sfc.judge("x", _paired(0.1, 0.01, 0.2, {"a": (100, -2.0, -0.1), "b": (100, -2.0, 0.1),
                                                      "c": (19, -2.0, -0.1)}))
        self.assertEqual(got["cells_worse_beyond_interval"], ["by_regime/a"])
        self.assertEqual(got["cells"]["by_regime/c"], "too few days")


if __name__ == "__main__":
    unittest.main()
