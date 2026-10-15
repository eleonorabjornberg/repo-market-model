"""The anchor's day type, the split of #741 (H1, step 3; H5 result pages).

B1 centres every lead on the anchor, the last public row. `anchor_day_type` labels a decision day by the
type of that row (`SplitDeclaration.reporting_day_type`), so a result against B1 can be split by whether B1
starts from a calendar spike. It adds no rule and changes no benchmark.

Mutation record, in a scratch copy of `src/repo_model/anchor_day_type.py`: `splits.reporting_day_type(panel[anchor]...)`
replaced by `splits.reporting_day_type(panel[decision_index]...)` (the decision day's own type, not the
anchor's). Failed with `AssertionError`: `test_the_label_is_the_type_of_the_row_before_the_decision_day`,
`test_a_quarter_end_anchor_is_labelled_as_one` and `test_the_many_day_form_is_keyed_by_decision_day`. No `LookAheadError` is expected: the label is read from a row
that `protocol_benchmarks` has already required to be public.
"""

from __future__ import annotations

import unittest
from datetime import date

import benchmark_simulation as sim
from repo_model.anchor_day_type import anchor_day_type, anchor_day_types

REGISTRY, SPLITS, DECISION = sim.REGISTRY, sim.SPLITS, sim.DECISION


class AnchorDayTypeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sample = sim.simulate(sim.ProcessSpec(), seed=741)
        cls.rows = cls.sample.rows
        cls.dates = [row.date for row in cls.rows]

    def test_the_label_is_the_type_of_the_row_before_the_decision_day(self):
        seen = set()
        for t in range(300, len(self.rows) - 5, 7):
            got = anchor_day_type(self.rows, t, registry=REGISTRY, decision_time=DECISION, splits=SPLITS)
            seen.add(got)
            self.assertEqual(got, self.sample.kinds[t - 1], self.dates[t])
        self.assertEqual(seen, {"ordinary", "tax_date", "month_end", "quarter_end"})

    def test_after_a_weekend_the_anchor_is_friday(self):
        t = self.dates.index(date(2020, 1, 6))
        self.assertEqual(self.dates[t - 1], date(2020, 1, 3))
        got = anchor_day_type(self.rows, t, registry=REGISTRY, decision_time=DECISION, splits=SPLITS)
        self.assertEqual(got, self.sample.kinds[t - 1])

    def test_a_quarter_end_anchor_is_labelled_as_one(self):
        t = self.dates.index(date(2021, 1, 4))
        self.assertEqual(self.dates[t - 1], date(2020, 12, 31))
        got = anchor_day_type(self.rows, t, registry=REGISTRY, decision_time=DECISION, splits=SPLITS)
        self.assertEqual(got, "quarter_end")

    def test_the_many_day_form_is_keyed_by_decision_day(self):
        days = [self.dates[t] for t in (300, 310, 320)]
        got = anchor_day_types(self.rows, days, registry=REGISTRY, decision_time=DECISION, splits=SPLITS)
        self.assertEqual(list(got), days)
        self.assertEqual(got[days[1]], self.sample.kinds[310 - 1])

    def test_a_day_not_on_the_panel_is_refused(self):
        with self.assertRaises(ValueError):
            anchor_day_types(self.rows, [date(2020, 1, 4)], registry=REGISTRY, decision_time=DECISION, splits=SPLITS)


if __name__ == "__main__":
    unittest.main()
