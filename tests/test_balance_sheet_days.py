"""Balance-sheet days (#427, track B of #374): the calendar rules, and FR 2004 as a release-time input.

The calendar rules are cited to their public source and gated on when that
source was public (`balance_sheet_days.RULES`). The FR 2004 net Treasury
position enters the design only through the as-of rule, which reads it at its
declared release (`nyfed_fr2004`'s six business days, 16:30 ET).

Recorded mutations (CLAUDE.md):

* `balance_sheet_days.require_public`: `if decision < rule.public_from:` mutated
  to `if False:`. `test_a_rule_is_not_used_before_its_source_was_public` then
  fails with `AssertionError: LookAheadError not raised`.
* `InformationRule.check` (asof.py): `if available > deadline:` mutated to
  `if False:`. `test_a_dealer_position_is_invisible_before_its_release` then
  fails with `AssertionError: LookAheadError not raised`.
"""

from __future__ import annotations

import json
import unittest
from datetime import date, datetime, time, timedelta
from pathlib import Path

from repo_model import balance_sheet_days as bsd
from repo_model import pressure_judge as pj
from repo_model.asof import InformationRule
from repo_model.data import DailyObservation, days_to_month_end, next_business_day, quarter_end, tax_date
from repo_model.splits import LookAheadError

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = json.loads((ROOT / "metadata" / "sources.json").read_text())


def weekdays(start, count, skip=()):
    out, when = [], start
    while len(out) < count:
        if when.weekday() < 5 and when not in skip:
            out.append(when)
        when += timedelta(days=1)
    return out


class RuleTests(unittest.TestCase):
    def test_every_rule_is_cited_to_a_public_https_source(self):
        for rule in bsd.RULES:
            self.assertTrue(rule.sources, rule.name)
            for url in rule.sources:
                self.assertTrue(url.startswith("https://"), rule.name)
            self.assertIsInstance(rule.public_from, date)

    def test_the_rules_are_public_before_the_panel_starts(self):
        for rule in bsd.RULES:
            self.assertLess(rule.public_from, date(2018, 4, 3), rule.name)

    def test_the_foreign_bank_quarter_end_run_up_is_the_last_business_days_of_the_quarter(self):
        # 2019-03-31 is a Sunday: the last business day is Friday the 29th.
        got = bsd.flags(date(2019, 3, 27), date(2019, 3, 26))
        self.assertEqual(got["foreign_bank_quarter_end"], 1.0)
        self.assertEqual(bsd.flags(date(2019, 3, 26), date(2019, 3, 25))["foreign_bank_quarter_end"], 0.0)
        self.assertEqual(bsd.flags(date(2019, 3, 29), date(2019, 3, 28))["foreign_bank_quarter_end"], 1.0)

    def test_the_month_end_rule_excludes_quarter_ends(self):
        self.assertEqual(bsd.flags(date(2019, 4, 30), date(2019, 4, 29))["foreign_bank_month_end"], 1.0)
        self.assertEqual(bsd.flags(date(2019, 3, 29), date(2019, 3, 28))["foreign_bank_month_end"], 0.0)

    def test_the_gsib_year_end_is_december_only(self):
        self.assertEqual(bsd.flags(date(2019, 12, 31), date(2019, 12, 30))["gsib_year_end"], 1.0)
        self.assertEqual(bsd.flags(date(2019, 12, 20), date(2019, 12, 19))["gsib_year_end"], 0.0)
        self.assertEqual(bsd.flags(date(2019, 9, 30), date(2019, 9, 27))["gsib_year_end"], 0.0)

    def test_a_flag_is_a_function_of_the_date_alone(self):
        for day in weekdays(date(2022, 1, 3), 120):
            self.assertEqual(bsd.flags(day, day - timedelta(days=1)), bsd.flags(day, day - timedelta(days=9)))

    def test_a_rule_is_not_used_before_its_source_was_public(self):
        """Recorded mutation: see the module docstring (`LookAheadError` not raised)."""

        with self.assertRaises(LookAheadError):
            bsd.flags(date(2018, 3, 29), date(2014, 1, 10))


class ScoredDayTests(unittest.TestCase):
    def calendar_values(self, day):
        return {"days_to_month_end": days_to_month_end(day), "quarter_end": quarter_end(day), "tax_date": tax_date(day)}

    def test_the_scored_day_is_recovered_from_its_calendar_columns(self):
        for anchor in weekdays(date(2019, 1, 2), 400):
            for ahead in range(1, 8):
                target = next_business_day(anchor, ahead)
                got = bsd.scored_day(anchor, self.calendar_values(target))
                self.assertEqual(got, target, (anchor, ahead))

    def test_a_calendar_that_matches_no_day_is_refused(self):
        with self.assertRaises(ValueError):
            bsd.scored_day(date(2019, 3, 4), {"days_to_month_end": 99.0, "quarter_end": 0.0, "tax_date": 0.0})


class DealerPositionReleaseTests(unittest.TestCase):
    """The FR 2004 net Treasury position, as the as-of rule reads it."""

    DATES = weekdays(date(2026, 1, 5), 40, skip={date(2026, 1, 19)})

    def rows(self):
        rows = []
        for index, when in enumerate(self.DATES):
            # A weekly Wednesday print, carried until the next, as the panel carries it.
            rows.append(
                DailyObservation(
                    when,
                    {"sofr": 2.0 + index / 100.0, "iorb": 2.0, "dealer_treasury_position": float(100 + 10 * (index // 5))},
                )
            )
        return rows

    def rule(self):
        return InformationRule(REGISTRY, ("spread_bps", "dealer_treasury_position"), decision_time=time(16, 0))

    def test_a_dealer_position_is_invisible_before_its_release(self):
        """Recorded mutation: see the module docstring (`LookAheadError` not raised)."""

        rule = self.rule()
        scored = self.DATES.index(date(2026, 1, 22))
        info = rule.information_set(self.DATES, scored)
        (read,) = [r for r in info.reads if r.feature == "dealer_treasury_position"]
        self.assertLessEqual(read.available_at, info.decision_instant)
        # The next row's print is released after the decision: reading it is leakage.
        newer = tuple(r._replace(row=r.row + 1) if r.feature == "dealer_treasury_position" else r for r in info.reads)
        with self.assertRaises(LookAheadError):
            rule.check(self.DATES, info._replace(reads=newer))

    def test_the_value_read_is_the_released_one(self):
        rule = self.rule()
        scored = self.DATES.index(date(2026, 1, 22))
        rows = self.rows()
        info = rule.information_set(self.DATES, scored)
        observation = rule.observation(rows, info)
        (read,) = [r for r in info.reads if r.feature == "dealer_treasury_position"]
        self.assertEqual(observation.values["dealer_treasury_position"], rows[read.row].values["dealer_treasury_position"])
        self.assertLess(read.row, scored)


class CandidateDeclarationTests(unittest.TestCase):
    """What is pinned is what was declared before any score (`metadata/pressure_judge.json`)."""

    def declared(self):
        return dict(pj.load_declaration().candidates)

    def test_the_declaration_carries_each_candidate_as_defined_here(self):
        from repo_model import balance_sheet_candidates as bc

        for name in bc.CANDIDATES:
            self.assertEqual(self.declared()[name], bc.declaration_entry(name), name)

    def test_each_candidate_extends_its_comparison_by_the_dealer_position_only(self):
        from repo_model import balance_sheet_candidates as bc

        comparison = {"balance_sheet_hierarchical_logistic": "hierarchical_logistic",
                      "balance_sheet_scarcity_gbm": "scarcity_gbm"}
        for name, base in comparison.items():
            extra = set(self.declared()[name]["features"]) - set(self.declared()[base]["features"])
            self.assertEqual(extra, {bc.POSITION}, name)

    def test_no_candidate_declares_a_fixed_cutoff(self):
        from repo_model import pressure_judge as pj

        for name in ("balance_sheet_hierarchical_logistic", "balance_sheet_scarcity_gbm"):
            self.assertNotIn("cutoffs", self.declared()[name])
        pj.load_declaration(ROOT / "metadata" / "pressure_judge.json")


if __name__ == "__main__":
    unittest.main()
