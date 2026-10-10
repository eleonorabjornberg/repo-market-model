"""The pressure audit's calendar and settlement rule (#473): choice on training windows only.

`scripts/pressure_audit.py` chooses, at each refit and horizon, which clauses of the declared rule
(`metadata/pressure_audit.json`) are on, from the refit's training window alone, as the judge chooses a
flag cut-off (`pressure_judge.choose_cutoffs`). These tests build small series so each rule has a known
answer.

**Recorded mutations** (CLAUDE.md: a new leakage guard carries one that kills it).

* The choice reads the training window alone. `select_clauses` refuses a window that reaches past the
  refit's training end. Mutation 1: in `scripts/pressure_audit.py::select_clauses`, replace `if late:` with
  `if False:`; the failing tests were `test_a_window_that_reaches_past_the_training_end_is_refused` and
  `test_a_window_with_a_day_but_no_training_end_is_refused`, which raised `AssertionError`
  (`LookAheadError not raised`).
* The training window of a block ends the business day before its first decision instant: the outcome of
  the decision day itself is published the next morning. Mutation 2: in `scripts/pressure_audit.py::training_end`,
  replace `last_known = position - horizon - 1` with `last_known = position - horizon`; the failing test was
  `test_training_ends_the_business_day_before_the_first_decision_instant`, which raised `AssertionError`
  (`datetime.date(2024, 1, 12) != datetime.date(2024, 1, 11)`).
* The settlement clause is a horizon-1 fact. Mutation 3: in `scripts/pressure_audit.py::clause_options`,
  replace `horizon in settlement["horizons"]` with `True` (in the line `on = variant == "calendar_settlement" and ...`); the failing test was
  `test_settlement_is_a_clause_only_at_horizon_one`, which raised `AssertionError`
  (`[None, 300, 250, 200, 150, 100, 75] != [None]`).
"""

from __future__ import annotations

import importlib.util
import json
import unittest
from datetime import date, timedelta
from pathlib import Path

from repo_model.splits import LookAheadError

REPO = Path(__file__).resolve().parents[1]


def _load():
    spec = importlib.util.spec_from_file_location("pressure_audit_script", REPO / "scripts" / "pressure_audit.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


audit = _load()
DECLARED = json.loads((REPO / "metadata" / "pressure_audit.json").read_text())


def _days(n, start=date(2024, 1, 1)):
    out, day = [], start
    while len(out) < n:
        if day.weekday() < 5:
            out.append(day)
        day += timedelta(days=1)
    return out


def _mask(bits):
    return sum(1 << k for k, b in enumerate(bits) if b)


class SelectionTests(unittest.TestCase):
    def setUp(self):
        self.days = _days(10)
        # Day 3 and day 7 are onsets (pressure days); day 5 is a plain pressure-free day.
        self.onset = _mask([0, 0, 0, 1, 0, 0, 0, 1, 0, 0])
        self.pressure = _mask([0, 0, 0, 1, 1, 0, 0, 1, 0, 0])
        self.options = {
            "quarter_end": {False: 0, True: _mask([0, 0, 0, 1, 0, 0, 0, 0, 0, 0])},
            "tax_date": {False: 0, True: _mask([0, 0, 0, 0, 0, 0, 0, 1, 0, 0])},
            "month_end_window": {None: 0, 0: _mask([1, 1, 0, 0, 0, 0, 0, 0, 0, 0])},
            "settlement": {None: 0},
        }

    def choose(self, **kwargs):
        args = dict(
            days=self.days, onset=self.onset, pressure=self.pressure, options=self.options,
            training_end=self.days[-1], limit=2.0,
        )
        args.update(kwargs)
        return audit.select_clauses(**args)

    def test_picks_the_clauses_with_the_highest_recall_within_the_limit(self):
        choice = self.choose()
        self.assertEqual(choice["quarter_end"], True)
        self.assertEqual(choice["tax_date"], True)

    def test_a_clause_that_only_adds_false_alarms_is_left_off(self):
        # The month-end window flags days 0 and 1, which are not pressure days, and catches no onset;
        # of two combinations with the same recall the one that flags fewer days wins.
        self.assertIsNone(self.choose()["month_end_window"])

    def test_the_limit_binds(self):
        # One false alarm per onset at most: 2 onsets allow 2 false alarms, so a clause with 3 is refused.
        wide = dict(self.options)
        wide["month_end_window"] = {None: 0, 0: _mask([1, 1, 1, 0, 0, 0, 0, 0, 0, 0]), 1: _mask([1, 1, 1, 1, 1, 1, 1, 1, 1, 1])}
        choice = self.choose(options=wide, limit=1.0)
        self.assertIsNone(choice["month_end_window"])

    def test_a_window_without_an_onset_flags_nothing(self):
        self.assertIsNone(self.choose(onset=0, pressure=0))

    def test_no_clause_within_the_limit_that_catches_an_onset_flags_nothing(self):
        every = {name: {key: _mask([1] * 10) if key not in (False, None) else 0 for key in values} for name, values in self.options.items()}
        self.assertIsNone(self.choose(options=every, limit=0.5))

    def test_a_window_that_reaches_past_the_training_end_is_refused(self):
        with self.assertRaises(LookAheadError):
            self.choose(training_end=self.days[-2])

    def test_a_window_with_a_day_but_no_training_end_is_refused(self):
        with self.assertRaises(LookAheadError):
            self.choose(training_end=None)


class TrainingEndTests(unittest.TestCase):
    def test_training_ends_the_business_day_before_the_first_decision_instant(self):
        calendar = _days(30)
        first = calendar[10]
        # Horizon 1: the decision is made on calendar[9]; SOFR for calendar[9] is published the morning after,
        # so the last outcome the refit can read is calendar[8].
        self.assertEqual(audit.training_end(calendar, first, 1), calendar[8])
        self.assertEqual(audit.training_end(calendar, first, 3), calendar[6])
        self.assertIsNone(audit.training_end(calendar, calendar[1], 1))


class OptionTests(unittest.TestCase):
    def test_settlement_is_a_clause_only_at_horizon_one(self):
        both = audit.clause_options(DECLARED, 1, "calendar_settlement")["settlement"]
        self.assertEqual(both, [None, 300, 250, 200, 150, 100, 75])
        for horizon in (2, 3, 4, 5):
            self.assertEqual(audit.clause_options(DECLARED, horizon, "calendar_settlement")["settlement"], [None])

    def test_the_calendar_variant_has_no_settlement_clause_at_any_horizon(self):
        for horizon in (1, 2, 3, 4, 5):
            self.assertEqual(audit.clause_options(DECLARED, horizon, "calendar")["settlement"], [None])


if __name__ == "__main__":
    unittest.main()
