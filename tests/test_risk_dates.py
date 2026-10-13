"""One definition of "not a risk date" (#682, finding #669), named, and every script reads it from one place.

Two definitions were in use. `SCHEDULED` is the judge's `risk_date` grouping: a quarter-end, a tax date or a coupon
settlement. `NON_ORDINARY` is the model's own rule (`ml._RiskDateDesign.member`, `announcement_dating_rescore.risk_flag`):
any day type other than `ordinary`, month-ends included, or a coupon settlement. They differ by the month-ends that are not
quarter-ends. Which one H2 and H5 use is Eleonora's ruling; this module only names both and gives each script one place to
ask.
"""

import importlib.util
import re
import sys
import unittest
from pathlib import Path

from repo_model import risk_dates
from repo_model.evaluation_splits import load_split_declaration

ROOT = Path(__file__).resolve().parents[1]
SPLITS = load_split_declaration(ROOT / "metadata" / "evaluation_splits.json")


def row(*, quarter_end=0.0, tax_date=0.0, days_to_month_end=10.0, coupons=0.0):
    return {
        "quarter_end": quarter_end,
        "tax_date": tax_date,
        "days_to_month_end": days_to_month_end,
        "treasury_settlement_coupons": coupons,
    }


class DefinitionTests(unittest.TestCase):
    def test_the_two_definitions_have_explicit_names(self):
        self.assertEqual(risk_dates.DEFINITIONS, ("scheduled", "non_ordinary"))

    def test_an_ordinary_day_is_not_a_risk_date_under_either(self):
        for definition in risk_dates.DEFINITIONS:
            self.assertFalse(risk_dates.is_risk_date(row(), definition, splits=SPLITS))

    def test_a_quarter_end_a_tax_date_and_a_coupon_settlement_are_risk_dates_under_both(self):
        for definition in risk_dates.DEFINITIONS:
            for kwargs in ({"quarter_end": 1.0}, {"tax_date": 1.0}, {"coupons": 2.0}):
                self.assertTrue(risk_dates.is_risk_date(row(**kwargs), definition, splits=SPLITS), (definition, kwargs))

    def test_a_month_end_that_is_not_a_quarter_end_is_where_they_differ(self):
        month_end = row(days_to_month_end=0.0)
        self.assertFalse(risk_dates.is_risk_date(month_end, "scheduled"))
        self.assertTrue(risk_dates.is_risk_date(month_end, "non_ordinary", splits=SPLITS))

    def test_the_coupon_clause_is_the_non_ordinary_rule_at_h_above_1(self):
        coupon_day = row(coupons=3.0)
        self.assertTrue(risk_dates.is_risk_date(coupon_day, "non_ordinary", splits=SPLITS, coupon_clause=True))
        self.assertFalse(risk_dates.is_risk_date(coupon_day, "non_ordinary", splits=SPLITS, coupon_clause=False))

    def test_a_missing_coupon_is_not_a_settlement(self):
        self.assertFalse(risk_dates.is_risk_date(row(coupons=None), "scheduled"))
        self.assertFalse(risk_dates.is_risk_date(row(coupons=None), "non_ordinary", splits=SPLITS))

    def test_an_unknown_definition_is_refused(self):
        with self.assertRaises(ValueError):
            risk_dates.is_risk_date(row(), "month_ends", splits=SPLITS)

    def test_non_ordinary_needs_the_split_declaration(self):
        with self.assertRaises(ValueError):
            risk_dates.is_risk_date(row(), "non_ordinary")

    def test_the_mask_is_true_where_the_day_is_not_a_risk_date(self):
        rows = [row(), row(quarter_end=1.0), row(days_to_month_end=0.0)]
        self.assertEqual(risk_dates.not_risk_date_mask(rows, "scheduled"), [True, False, True])
        self.assertEqual(risk_dates.not_risk_date_mask(rows, "non_ordinary", splits=SPLITS), [True, False, False])


class CallersTests(unittest.TestCase):
    """The scripts and the judge read the definition from here, so they cannot drift apart again."""

    def test_the_judge_grouping_is_the_scheduled_definition(self):
        from repo_model import pressure_judge as pj

        for kwargs in ({}, {"quarter_end": 1.0}, {"tax_date": 1.0}, {"coupons": 1.0}, {"days_to_month_end": 0.0}):
            self.assertEqual(
                pj._scheduled_risk_date(row(**kwargs)), risk_dates.is_risk_date(row(**kwargs), "scheduled"), kwargs
            )

    def test_risk_flag_is_the_non_ordinary_definition(self):
        sys.path.insert(0, str(ROOT / "src"))
        spec = importlib.util.spec_from_file_location(
            "announcement_dating_rescore_script", ROOT / "scripts" / "announcement_dating_rescore.py"
        )
        ann = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(ann)

        for kwargs in ({}, {"quarter_end": 1.0}, {"tax_date": 1.0}, {"coupons": 1.0}, {"days_to_month_end": 0.0}):
            for clause in (True, False):
                self.assertEqual(
                    ann.risk_flag(SPLITS, row(**kwargs), clause),
                    risk_dates.is_risk_date(row(**kwargs), "non_ordinary", splits=SPLITS, coupon_clause=clause),
                    (kwargs, clause),
                )

    def test_no_script_writes_its_own_risk_date_rule(self):
        """A script that tests `day_type(...) != "ordinary"` has its own copy of the rule; ask `risk_dates` instead."""

        own_rule = re.compile(r"(?<!reporting_)day_type(\([^)]*\))?\s*(!=|==)\s*[\"']ordinary[\"']")
        offenders = []
        for path in sorted((ROOT / "scripts").glob("*.py")):
            for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
                if own_rule.search(line):
                    offenders.append(f"{path.name}:{number}")
        self.assertEqual(offenders, [], "these scripts spell the risk-date rule out; call repo_model.risk_dates")


if __name__ == "__main__":
    unittest.main()
