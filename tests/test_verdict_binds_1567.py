"""#1567 (H5.M5 / H1, the scorer; audit item 3 of #1554; Eleonora's ruling of 11 November 2026, card f1554-3-verdict-1111,
option (a) "bind"): `scoring_protocol.verdict` binds what protocol v1 requires, and `enforce_coverage_requirement` no longer passes on
nothing.

The audit's reproduction: a verdict was returned for (1) two tests on arbitrary scores that nothing identified as B1 and B2, (2) days
long before any confirmation day and (3) with no coverage check at all; and `enforce_coverage_requirement([], ...)`, or a list
with no cell of the rule, returned `[]`, the same as a pass. `ReproductionTests` runs each; every one now raises.

Each new guard has one recorded mutation, made on this branch's tree and reverted (2026-11-11):

- benchmark identity: in `verdict`, the loop `for name, test in (("B1", against_b1), ("B2", against_b2)): if test.benchmark != name`
  became `if False`; `BenchmarkIdentityTests.test_a_test_not_labelled_b1_is_refused` raised `AssertionError: ProtocolError not raised`.
- prospective days: in `_require_prospective`, `if early:` became `if False:`; `ProspectiveDayTests.test_a_day_before_the_first_confirmation_day_is_refused`
  raised `AssertionError: LookAheadError not raised`.
- locked day: in `_require_prospective`, deleting the `lockbox.require_unlocked(days, where=where)` line; `ProspectiveDayTests.test_a_locked_day_is_refused`
  raised `AssertionError: LookAheadError not raised`.
- coverage passed: in `verdict`, deleting the `_require_coverage_passed(coverage)` line;
  `CoverageBindingTests.test_a_verdict_without_a_coverage_check_is_refused` raised `AssertionError: ProtocolError not raised`.
- empty list and no cell of the rule: in `enforce_coverage_requirement`, `if not read:` became `if False:`;
  `EnforceRefusesNothingTests.test_an_empty_list_is_refused` raised `AssertionError: ValueError not raised`, and so did
  `test_cells_of_another_rule_only_are_refused` (one line guards both).
- mixed methods: `if len(methods) > 1:` became `if False:`; `test_cells_of_several_methods_are_refused` raised `AssertionError: ValueError not raised`.
- empty sample: `if empty:` became `if False:`; `test_a_cell_with_no_sample_is_refused` raised `AssertionError: ValueError not raised`.
"""

from __future__ import annotations

import dataclasses
import random
import unittest
from datetime import date
from unittest import mock

from repo_model import lockbox
from repo_model import scoring_protocol as sp
from repo_model.splits import LookAheadError

from test_scoring_protocol import weekdays
from test_scoring_protocol_coverage_requirement import world

FIRST_DAY = date(2015, 1, 2)


def passed_coverage(method="spaced"):
    """A coverage check that passed: calibrated cells, read under the design the requirement names."""

    forecasts, outcomes, calendar, labels = world(n=2000, seed=5)
    cells = sp.coverage_cells(forecasts, outcomes, calendar, labels, method=method)
    return sp.check_coverage_requirement(cells, alpha=0.001, family="per_cell", rule="strict")


def labelled_tests(days=None, seed=9):
    """A candidate that beats B1 and B2 on 250 days, as the verdict's own tests make them."""

    rng = random.Random(seed)
    days = days or weekdays(FIRST_DAY, 250)
    scores = lambda level: {day: level + 0.05 * rng.gauss(0, 1) for day in days}
    b1, b2, strong = scores(1.0), scores(1.2), scores(0.8)
    return sp.paired_tests([(b1, strong), (b2, strong)], seed=1, draws=200, benchmarks=("B1", "B2"))


class BoundVerdictTests(unittest.TestCase):
    def test_a_bound_verdict_is_read(self):
        b1, b2 = labelled_tests()
        self.assertEqual(
            sp.verdict(b1, b2, look=3, first_confirmation_day=FIRST_DAY, coverage=passed_coverage()), sp.SUPPORTED
        )


class BenchmarkIdentityTests(unittest.TestCase):
    def test_a_test_not_labelled_b1_is_refused(self):
        b1, b2 = labelled_tests()
        for first, second in ((dataclasses.replace(b1, benchmark=None), b2), (b2, b1), (b1, dataclasses.replace(b2, benchmark="B3"))):
            with self.subTest(first=first.benchmark, second=second.benchmark):
                with self.assertRaises(sp.ProtocolError):
                    sp.verdict(first, second, look=3, first_confirmation_day=FIRST_DAY, coverage=passed_coverage())

    def test_a_name_outside_the_protocol_is_refused_when_the_tests_are_made(self):
        days = weekdays(FIRST_DAY, 250)
        scores = {day: 1.0 + 0.01 * i for i, day in enumerate(days)}
        with self.assertRaises(sp.ProtocolError):
            sp.paired_tests([(scores, scores)], seed=1, draws=10, benchmarks=("B9",))
        with self.assertRaises(sp.ProtocolError):
            sp.paired_tests([(scores, scores)], seed=1, draws=10, benchmarks=("B1", "B2"))

    def test_the_b3_comparison_must_be_b3(self):
        b1, b2 = labelled_tests()
        b3 = dataclasses.replace(b1, benchmark="B3")
        sp.report(b1, b2, b3, look=3, first_confirmation_day=FIRST_DAY, coverage=passed_coverage())
        with self.assertRaises(sp.ProtocolError):
            sp.report(b1, b2, b1, look=3, first_confirmation_day=FIRST_DAY, coverage=passed_coverage())


class ProspectiveDayTests(unittest.TestCase):
    def test_a_day_before_the_first_confirmation_day_is_refused(self):
        b1, b2 = labelled_tests()
        with self.assertRaises(LookAheadError):
            sp.verdict(b1, b2, look=3, first_confirmation_day=b1.days[1], coverage=passed_coverage())

    def test_a_locked_day_is_refused(self):
        b1, b2 = labelled_tests()
        locked = lockbox.LockboxTier("test_blind", b1.days[0], None, None)
        with mock.patch.object(lockbox, "load_lockbox", return_value=(locked,)):
            with self.assertRaises(LookAheadError):
                sp.verdict(b1, b2, look=3, first_confirmation_day=FIRST_DAY, coverage=passed_coverage())

    def test_the_registration_day_must_be_a_date(self):
        b1, b2 = labelled_tests()
        with self.assertRaises(sp.ProtocolError):
            sp.verdict(b1, b2, look=3, first_confirmation_day="2015-01-02", coverage=passed_coverage())


class CoverageBindingTests(unittest.TestCase):
    def test_a_verdict_without_a_coverage_check_is_refused(self):
        b1, b2 = labelled_tests()
        forged = sp.CoverageCheck(0.05, "holm", "strict", "spaced", 1)
        for coverage in (None, True, forged):
            with self.subTest(coverage=coverage):
                with self.assertRaises(sp.ProtocolError):
                    sp.verdict(b1, b2, look=3, first_confirmation_day=FIRST_DAY, coverage=coverage)

    def test_a_check_on_the_wrong_method_does_not_bind(self):
        b1, b2 = labelled_tests()
        with self.assertRaises(sp.ProtocolError):
            passed_coverage(method="thinned")
        thinned = dataclasses.replace(passed_coverage(), method="thinned")
        with self.assertRaises(sp.ProtocolError):
            sp.verdict(b1, b2, look=3, first_confirmation_day=FIRST_DAY, coverage=thinned)

    def test_a_check_is_not_made_while_the_requirement_is_off(self):
        forecasts, outcomes, calendar, labels = world(n=2000, seed=5)
        cells = sp.coverage_cells(forecasts, outcomes, calendar, labels, method="spaced")
        with mock.patch.object(sp, "COVERAGE_REQUIREMENT_IN_FORCE", False):
            with self.assertRaises(sp.ProtocolError):
                sp.check_coverage_requirement(cells, alpha=0.05, family="holm", rule="strict")

    def test_a_failing_forecast_gets_no_check(self):
        forecasts, outcomes, calendar, labels = world(n=300, outcome=lambda day: 4.9)
        cells = sp.coverage_cells(forecasts, outcomes, calendar, labels, method="spaced")
        with self.assertRaises(sp.CoverageRequirementFailed):
            sp.check_coverage_requirement(cells, alpha=0.05, family="holm", rule="strict")


class EnforceRefusesNothingTests(unittest.TestCase):
    def cells(self, method="spaced"):
        forecasts, outcomes, calendar, labels = world(n=2000, seed=5)
        return sp.coverage_cells(forecasts, outcomes, calendar, labels, method=method)

    def enforce(self, cells):
        return sp.enforce_coverage_requirement(cells, alpha=0.001, family="per_cell", rule="strict")

    def test_an_empty_list_is_refused(self):
        with self.assertRaises(ValueError):
            self.enforce([])

    def test_cells_of_another_rule_only_are_refused(self):
        with self.assertRaises(ValueError):
            self.enforce([c for c in self.cells() if c.rule != "strict"])

    def test_cells_of_several_methods_are_refused(self):
        mixed = self.cells("spaced") + self.cells("thinned")
        with self.assertRaises(ValueError):
            self.enforce(mixed)

    def test_a_cell_with_no_sample_is_refused(self):
        cells = self.cells()
        empty = dataclasses.replace(cells[0], rule="strict", n=0, hits=0, kupiec_p=1.0)
        with self.assertRaises(ValueError):
            self.enforce([empty] + [c for c in cells if c.rule == "strict"][1:])

    def test_a_good_list_still_passes_and_other_rules_beside_it_are_ignored(self):
        self.assertEqual(self.enforce(self.cells()), [])

    def test_the_flag_off_is_still_inert(self):
        with mock.patch.object(sp, "COVERAGE_REQUIREMENT_IN_FORCE", False):
            self.assertEqual(self.enforce([]), [])


class ReproductionTests(unittest.TestCase):
    """The audit's reproduction: each of the unbound calls that used to return now raises."""

    def test_the_reproduction_raises(self):
        days = weekdays(date(2015, 1, 2), 250)
        rng = random.Random(3)
        scores = lambda level: {day: level + 0.05 * rng.gauss(0, 1) for day in days}
        a, b, c = scores(1.0), scores(1.2), scores(0.8)
        tests = sp.paired_tests([(a, c), (b, c)], seed=1, draws=200)  # no identity declared
        with self.assertRaises(sp.ProtocolError):
            sp.verdict(tests[0], tests[1], look=3, first_confirmation_day=FIRST_DAY, coverage=passed_coverage())
        with self.assertRaises(TypeError):  # no registration day, no coverage check
            sp.verdict(tests[0], tests[1], look=3)
        with self.assertRaises(ValueError):
            sp.enforce_coverage_requirement([], alpha=0.05, family="holm", rule="strict")


if __name__ == "__main__":
    unittest.main()
