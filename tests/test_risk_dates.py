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
from datetime import date
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

    def test_the_scheduled_grouping_lives_here_and_the_judge_no_longer_defines_it(self):
        """Stage 1 of #1055: `pressure_judge._scheduled_risk_date` moved into `risk_dates`.

        The judge's grouping reads `risk_dates.scheduled_risk_date`, so the module that is retired later (stage 3)
        holds no copy of the definition.
        """

        from repo_model import pressure_judge as pj

        self.assertFalse(hasattr(pj, "_scheduled_risk_date"))
        for kwargs in ({}, {"quarter_end": 1.0}, {"tax_date": 1.0}, {"coupons": 1.0}, {"days_to_month_end": 0.0}):
            self.assertEqual(
                risk_dates.scheduled_risk_date(row(**kwargs)), risk_dates.is_risk_date(row(**kwargs), "scheduled"), kwargs
            )
        self.assertTrue(risk_dates.scheduled_risk_date(row(quarter_end=1.0)))
        self.assertFalse(risk_dates.scheduled_risk_date(row()))

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

    def test_the_reporting_reading_asks_the_reporting_day_type_of_the_date(self):
        """`reporting_on=` reads the day type as `reporting_day_type` does (the month's last two business days), #800.

        2024-03-27 is a reporting month-end (Good Friday, 29 March, is a holiday) that is four calendar days from the month's
        end, so the calendar-day window of `day_type` calls it ordinary.
        """

        day = date(2024, 3, 27)
        values = row(days_to_month_end=4.0)
        self.assertFalse(risk_dates.is_risk_date(values, "non_ordinary", splits=SPLITS))
        self.assertTrue(risk_dates.is_risk_date(values, "non_ordinary", splits=SPLITS, reporting_on=day))
        coupon = row(days_to_month_end=10.0, coupons=3.0)
        self.assertTrue(risk_dates.is_risk_date(coupon, "non_ordinary", splits=SPLITS, reporting_on=date(2024, 3, 12)))
        self.assertFalse(
            risk_dates.is_risk_date(coupon, "non_ordinary", splits=SPLITS, coupon_clause=False, reporting_on=date(2024, 3, 12))
        )

    def test_the_reporting_reading_is_for_the_reconciled_definition_only(self):
        with self.assertRaises(ValueError):
            risk_dates.is_risk_date(row(), "scheduled", reporting_on=date(2024, 3, 27))

    def test_h5_and_h6_ask_risk_dates_for_their_risk_day(self):
        """`spread_mr_variants.is_risk_day` and `risk_date_spread.risk_day_type` decide through `risk_dates` (#800)."""

        import inspect

        from repo_model import risk_date_spread, spread_mr_variants
        from repo_model.data import DailyObservation

        for function in (spread_mr_variants.is_risk_day, risk_date_spread.risk_day_type):
            self.assertIn("risk_dates.is_risk_date(", inspect.getsource(function), function.__qualname__)

        for when, kwargs in (
            (date(2024, 3, 12), {}),
            (date(2024, 3, 12), {"coupons": 3.0}),
            (date(2024, 3, 27), {"days_to_month_end": 4.0}),
            (date(2024, 3, 28), {"days_to_month_end": 3.0}),
            (date(2024, 3, 31), {"quarter_end": 1.0, "days_to_month_end": 0.0}),
            (date(2024, 4, 15), {"tax_date": 1.0}),
        ):
            values = row(**kwargs)
            expected = risk_dates.is_risk_date(values, "non_ordinary", splits=SPLITS, reporting_on=when)
            observation = DailyObservation(when, values)
            self.assertEqual(spread_mr_variants.is_risk_day(observation, SPLITS), expected, (when, kwargs))
            self.assertEqual(risk_date_spread.risk_day_type(when, values, SPLITS) is not None, expected, (when, kwargs))

    def test_no_script_writes_its_own_risk_date_rule(self):
        """A script that tests `day_type(...) != "ordinary"` has its own copy of the rule; ask `risk_dates` instead."""

        own_rule = re.compile(r"(?<!reporting_)day_type(\([^)]*\))?\s*(!=|==)\s*[\"']ordinary[\"']")
        # Scripts that group by the reporting day type, a third population the reconciliation doc names and
        # leaves alone (re-pointing them would move published figures): #686 joined main after this directive began.
        reporting_population = {"spread_mean_reversion_686.py"}
        offenders = []
        for path in sorted((ROOT / "scripts").glob("*.py")):
            if path.name in reporting_population:
                continue
            for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
                if own_rule.search(line):
                    offenders.append(f"{path.name}:{number}")
        self.assertEqual(offenders, [], "these scripts spell the risk-date rule out; call repo_model.risk_dates")


if __name__ == "__main__":
    unittest.main()
