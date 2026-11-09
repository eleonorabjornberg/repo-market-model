"""The coverage requirement of amendment 4 (#1130), put in force by #1522.

`docs/decisions/scoring-protocol.md`, section "Draft amendment 4", sets passing the Kupiec and Christoffersen tests
at q05/q95 and q01/q99, by lead and regime, as a registration requirement. Its in-force state is the record's: the
section says whether `scoring_protocol.COVERAGE_REQUIREMENT_IN_FORCE` is True, which hit rule the requirement reads
and which size table meets its point 3, and `InForceTests` checks the flag against that statement (the flag is True
only with the record saying so, and the record says so only with the flag True). While the flag is off,
`enforce_coverage_requirement` returns nothing whatever the cells say; `coverage_cells` only reports. The statistics are
`repo_model.coverage_tests` (#993); this module tests only what is new: the hit direction in each tail, both hit
rules, thinning, the HAC variant, the lockbox refusal and the inertness.

**Recorded mutation (flag).** `COVERAGE_REQUIREMENT_IN_FORCE = True` -> `False` in `scoring_protocol.py` fails
`InForceTests.test_the_flag_matches_the_record` with `AssertionError`.
**Recorded mutation (lower tail).** In `coverage_cells`, mapping a lower level to the upper-tail hit (`y > q`
instead of `y < q`) fails `HitDirectionTests.test_a_lower_level_is_hit_below_the_quantile` with `AssertionError`.
**Recorded mutation (lockbox).** Deleting the `lockbox.require_unlocked` call in `coverage_cells` fails
`LockboxTests.test_a_locked_day_is_refused` with `AssertionError: LookAheadError not raised`.
"""

from __future__ import annotations

import random
import unittest
from datetime import date, timedelta
from pathlib import Path
from unittest import mock

from repo_model import coverage_tests as ct
from repo_model import scoring_protocol as sp
from repo_model.splits import LookAheadError

RECORD = Path(__file__).resolve().parents[1] / "docs" / "decisions" / "scoring-protocol.md"
HEADING = "## Draft amendment 4: passing the coverage tests is a registration requirement (#1130)"


def business_days(count, start=date(2005, 1, 3)):
    days, day = [], start
    while len(days) < count:
        if day.weekday() < 5:
            days.append(day)
        day += timedelta(days=1)
    return days


def flat_quantiles(centre=0.0):
    """23 quantiles of a unit-width spread around `centre`, increasing, on the protocol's grid."""

    return [centre + (level - 0.5) * 10.0 for level in sp.GRID]


def world(n=400, seed=1, regimes=None, outcome=None):
    calendar = business_days(n + 6)
    rng = random.Random(seed)
    forecasts = {day: {h: flat_quantiles() for h in sp.HORIZONS} for day in calendar[:n]}
    outcomes = {day: (outcome(day) if outcome else rng.uniform(-5.0, 5.0)) for day in calendar}
    labels = {day: (regimes(day) if regimes else "all") for day in calendar[:n]}
    return forecasts, outcomes, calendar, labels


def cell(cells, **keys):
    found = [c for c in cells if all(getattr(c, k) == v for k, v in keys.items())]
    assert len(found) == 1, (keys, found)
    return found[0]


class HitDirectionTests(unittest.TestCase):
    def test_a_lower_level_is_hit_below_the_quantile(self):
        # Outcomes uniform on (-5, 5) against a forecast whose q05 is -4.5: about 5% fall below it, none above.
        forecasts, outcomes, calendar, labels = world(n=600)
        cells = sp.coverage_cells(forecasts, outcomes, calendar, labels, method="thinned")
        lower = cell(cells, level=0.05, lead=1, regime="all", rule="strict")
        upper = cell(cells, level=0.95, lead=1, regime="all", rule="strict")
        self.assertGreater(lower.hits, 0)
        self.assertLess(abs(lower.hits / lower.n - 0.05), 0.04)
        self.assertLess(abs(upper.hits / upper.n - 0.05), 0.04)
        # The same outcomes pushed all high: the upper level is hit often, the lower never.
        forecasts, outcomes, calendar, labels = world(n=600, outcome=lambda day: 4.9)
        cells = sp.coverage_cells(forecasts, outcomes, calendar, labels, method="thinned")
        self.assertEqual(cell(cells, level=0.05, lead=1, regime="all", rule="strict").hits, 0)
        self.assertEqual(cell(cells, level=0.95, lead=1, regime="all", rule="strict").hits,
                         cell(cells, level=0.95, lead=1, regime="all", rule="strict").n)

    def test_both_hit_rules_are_reported_and_differ_on_a_tie(self):
        # The outcome sits exactly on q95 (4.5) every day: y > q is never a hit, y >= q always is.
        forecasts, outcomes, calendar, labels = world(n=100, outcome=lambda day: 4.5)
        cells = sp.coverage_cells(forecasts, outcomes, calendar, labels, method="thinned")
        strict = cell(cells, level=0.95, lead=1, regime="all", rule="strict")
        tie = cell(cells, level=0.95, lead=1, regime="all", rule="tie_counts")
        self.assertEqual(strict.hits, 0)
        self.assertEqual(tie.hits, tie.n)
        # and the lower mirror: on q05 (-4.5) y < q never, y <= q always.
        forecasts, outcomes, calendar, labels = world(n=100, outcome=lambda day: -4.5)
        cells = sp.coverage_cells(forecasts, outcomes, calendar, labels, method="thinned")
        self.assertEqual(cell(cells, level=0.05, lead=1, regime="all", rule="strict").hits, 0)
        low = cell(cells, level=0.05, lead=1, regime="all", rule="tie_counts")
        self.assertEqual(low.hits, low.n)

    def test_the_levels_are_the_four_the_amendment_names(self):
        forecasts, outcomes, calendar, labels = world(n=60)
        cells = sp.coverage_cells(forecasts, outcomes, calendar, labels, method="thinned")
        self.assertEqual({c.level for c in cells}, {0.01, 0.05, 0.95, 0.99})
        self.assertEqual({c.lead for c in cells}, set(sp.HORIZONS))
        self.assertEqual({c.rule for c in cells}, {"strict", "tie_counts"})


class CellTests(unittest.TestCase):
    def test_cells_are_by_lead_and_regime(self):
        forecasts, outcomes, calendar, labels = world(
            n=200, regimes=lambda day: "calm" if day < calendar_split() else "stress"
        )
        cells = sp.coverage_cells(forecasts, outcomes, calendar, labels, method="thinned")
        self.assertEqual({c.regime for c in cells}, {"calm", "stress"})
        self.assertEqual(len(cells), 4 * 5 * 2 * 2)

    def test_a_too_narrow_forecast_fails_unconditional_coverage(self):
        # Outcomes uniform on (-10, 10) against a (-5, 5) forecast: the q05 and q95 are hit about 25% of the time.
        rng = random.Random(3)
        forecasts, outcomes, calendar, labels = world(n=500, outcome=lambda day: rng.uniform(-10.0, 10.0))
        cells = sp.coverage_cells(forecasts, outcomes, calendar, labels, method="thinned")
        self.assertLess(cell(cells, level=0.95, lead=1, regime="all", rule="strict").kupiec_p, 1e-6)
        self.assertLess(cell(cells, level=0.05, lead=1, regime="all", rule="strict").kupiec_p, 1e-6)

    def test_thinning_keeps_every_hth_decision_day(self):
        forecasts, outcomes, calendar, labels = world(n=300)
        cells = sp.coverage_cells(forecasts, outcomes, calendar, labels, method="thinned")
        n1 = cell(cells, level=0.05, lead=1, regime="all", rule="strict").n
        n3 = cell(cells, level=0.05, lead=3, regime="all", rule="strict").n
        n5 = cell(cells, level=0.05, lead=5, regime="all", rule="strict").n
        self.assertEqual(n1, 300)
        self.assertEqual(n3, 100)
        self.assertEqual(n5, 60)

    def test_hac_keeps_every_day_and_widens_the_test_under_dependent_hits(self):
        # Hits that come in runs of five (overlap): the naive Kupiec rejects, the HAC z-test is far less sure.
        runs = {}

        def outcome(day):
            block = (day - date(2005, 1, 3)).days // 7
            runs.setdefault(block, random.Random(block).random() < 0.05)
            return 4.9 if runs[block] else 0.0

        forecasts, outcomes, calendar, labels = world(n=500, outcome=outcome)
        thin = cell(sp.coverage_cells(forecasts, outcomes, calendar, labels, method="thinned"),
                    level=0.95, lead=5, regime="all", rule="strict")
        hac = cell(sp.coverage_cells(forecasts, outcomes, calendar, labels, method="hac"),
                   level=0.95, lead=5, regime="all", rule="strict")
        self.assertEqual(hac.n, 500)
        self.assertEqual(thin.n, 100)
        naive = ct.kupiec(
            ct.hit_sequence([outcomes[calendar[i + 5]] for i in range(500)], [4.5] * 500, rule="above"), 0.05
        )
        self.assertLess(naive.p_value, hac.kupiec_p)

    def test_hac_matches_the_plain_z_test_when_hits_are_independent(self):
        # lag 0 (lead 1) is the iid score test; its p-value is close to Kupiec's on a calibrated sequence.
        forecasts, outcomes, calendar, labels = world(n=2000, seed=11)
        hac = cell(sp.coverage_cells(forecasts, outcomes, calendar, labels, method="hac"),
                   level=0.95, lead=1, regime="all", rule="strict")
        self.assertGreater(hac.kupiec_p, 0.001)

    def test_the_method_has_no_default(self):
        forecasts, outcomes, calendar, labels = world(n=30)
        with self.assertRaises(TypeError):
            sp.coverage_cells(forecasts, outcomes, calendar, labels)
        with self.assertRaises(sp.ProtocolError):
            sp.coverage_cells(forecasts, outcomes, calendar, labels, method="neither")

    def test_a_day_without_a_regime_label_is_refused(self):
        forecasts, outcomes, calendar, labels = world(n=30)
        labels.pop(calendar[3])
        with self.assertRaises(sp.ProtocolError):
            sp.coverage_cells(forecasts, outcomes, calendar, labels, method="thinned")


def calendar_split():
    return business_days(100)[-1]


class LockboxTests(unittest.TestCase):
    def test_a_locked_day_is_refused(self):
        forecasts, outcomes, calendar, labels = world(n=30)
        with mock.patch.object(sp.lockbox, "require_unlocked", side_effect=LookAheadError("locked")) as guard:
            with self.assertRaises(LookAheadError):
                sp.coverage_cells(forecasts, outcomes, calendar, labels, method="thinned")
        self.assertEqual(guard.call_count, 1)


def record_section():
    text = RECORD.read_text(encoding="utf-8")
    start = text.index(HEADING)
    end = text.find("\n## ", start + len(HEADING))
    return " ".join(text[start:end if end != -1 else None].split())


class InForceTests(unittest.TestCase):
    def test_the_flag_matches_the_record(self):
        section = record_section()
        # Amendment 4 is in force as set (#1522, GO #1522): the record says the flag is True, names the hit rule, and the flag is True.
        self.assertIn("`scoring_protocol.COVERAGE_REQUIREMENT_IN_FORCE` is True", section)
        self.assertNotIn("`scoring_protocol.COVERAGE_REQUIREMENT_IN_FORCE` is False", section)
        self.assertTrue(sp.COVERAGE_REQUIREMENT_IN_FORCE)

    def test_the_record_names_the_hit_rule_the_requirement_reads(self):
        section = record_section()
        self.assertIn("reads the `strict` hit rule", section)
        self.assertIn("`tie_counts`", section)
        self.assertIn("randomised", section)

    def test_the_record_cites_the_size_table_that_meets_point_3(self):
        section = record_section()
        self.assertIn("PR #1520", section)
        self.assertIn("1.7%", section)
        self.assertIn("5.0%", section)

    def test_a_failing_forecast_raises_under_the_design_as_set_with_no_patch(self):
        forecasts, outcomes, calendar, labels = world(n=300, outcome=lambda day: 4.9)
        cells = sp.coverage_cells(forecasts, outcomes, calendar, labels, method="thinned")
        with self.assertRaises(sp.CoverageRequirementFailed):
            sp.enforce_coverage_requirement(cells, alpha=0.05, family="holm", rule="strict")


class InertWhileOffTests(unittest.TestCase):
    """The guard's inertness is a property of the flag, tested with the flag patched off."""

    def failing_cells(self):
        forecasts, outcomes, calendar, labels = world(n=300, outcome=lambda day: 4.9)
        return sp.coverage_cells(forecasts, outcomes, calendar, labels, method="thinned")

    def test_enforcement_returns_nothing_while_off(self):
        cells = self.failing_cells()
        with mock.patch.object(sp, "COVERAGE_REQUIREMENT_IN_FORCE", False):
            self.assertEqual(sp.enforce_coverage_requirement(cells, alpha=0.01, family="per_cell", rule="strict"), [])

    def test_enforcement_names_the_failing_cells_once_on(self):
        cells = self.failing_cells()
        with mock.patch.object(sp, "COVERAGE_REQUIREMENT_IN_FORCE", True):
            with self.assertRaises(sp.CoverageRequirementFailed) as raised:
                sp.enforce_coverage_requirement(cells, alpha=0.01, family="per_cell", rule="strict")
        self.assertIn("0.05", str(raised.exception))

    def test_a_calibrated_forecast_passes_once_on(self):
        forecasts, outcomes, calendar, labels = world(n=2000, seed=5)
        cells = sp.coverage_cells(forecasts, outcomes, calendar, labels, method="thinned")
        with mock.patch.object(sp, "COVERAGE_REQUIREMENT_IN_FORCE", True):
            self.assertEqual(sp.enforce_coverage_requirement(cells, alpha=0.001, family="per_cell", rule="strict"), [])

    def test_family_and_alpha_have_no_default(self):
        with self.assertRaises(TypeError):
            sp.enforce_coverage_requirement([])
        with self.assertRaises(sp.ProtocolError):
            sp.enforce_coverage_requirement([], alpha=0.01, family="other", rule="strict")

    def test_the_hit_rule_has_no_default_while_the_record_leaves_it_open(self):
        with self.assertRaises(TypeError):
            sp.enforce_coverage_requirement([], alpha=0.05, family="holm")

    def test_holm_is_a_family_option(self):
        cells = self.failing_cells()
        with mock.patch.object(sp, "COVERAGE_REQUIREMENT_IN_FORCE", True):
            with self.assertRaises(sp.CoverageRequirementFailed):
                sp.enforce_coverage_requirement(cells, alpha=0.05, family="holm", rule="strict")


if __name__ == "__main__":
    unittest.main()
