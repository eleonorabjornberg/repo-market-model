"""The sensitivity variants of the construction-gap sizing (#485) change one thing each, and only that.

`scripts/construction_gaps_485.py` is a scratch measurement. Its `declared` variant must be the declared
risk-date model, and every other variant a superset of its risk dates, so a difference in a table is the
change and not a different model.
"""

import importlib.util
import sys
import unittest
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from repo_model.data import DailyObservation  # noqa: E402
from repo_model.evaluation_splits import load_split_declaration  # noqa: E402

SPEC = importlib.util.spec_from_file_location("construction_gaps_485", ROOT / "scripts" / "construction_gaps_485.py")
SCRIPT = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(SCRIPT)

SPLITS = load_split_declaration(ROOT / "metadata" / "evaluation_splits.json")
FEATURES = (
    "spread_bps",
    "days_to_month_end",
    "quarter_end",
    "tax_date",
    "reserve_balances",
    "reserve_scarcity_state",
    "tga",
    "treasury_settlement",
    "treasury_settlement_coupons",
)


def values(day: date, *, coupons=0.0, bills=0.0, quarter_end=0.0, tax_date=0.0, to_month_end=15.0):
    return {
        "spread_bps": 1.0,
        "days_to_month_end": to_month_end,
        "quarter_end": quarter_end,
        "tax_date": tax_date,
        "reserve_balances": 3000.0,
        "reserve_scarcity_state": 1.0,
        "tga": 500.0,
        "treasury_settlement": coupons + bills,
        "treasury_settlement_coupons": coupons,
    }


# Days chosen for what they are: an ordinary mid-month Tuesday with a bill settlement (2019-08-13), the
# fourth-last business day of June 2019 (2019-06-25), the second-last business day of December 2018
# (2018-12-28, three calendar days from month-end), a coupon day (2019-01-15) and a plain day (2019-02-05).
CASES = {
    date(2019, 8, 13): values(date(2019, 8, 13), bills=90.0, to_month_end=18.0),
    date(2019, 6, 25): values(date(2019, 6, 25), bills=75.0, to_month_end=5.0),
    date(2018, 12, 28): values(date(2018, 12, 28), coupons=18.0, to_month_end=3.0),
    date(2019, 1, 15): values(date(2019, 1, 15), coupons=78.0, bills=70.0, to_month_end=16.0),
    date(2019, 2, 5): values(date(2019, 2, 5), to_month_end=23.0),
}


class VariantRiskDateSets(unittest.TestCase):
    def test_the_control_is_the_declared_rule(self):
        for day, row in CASES.items():
            for h in (1, 2, 5):
                self.assertEqual(
                    SCRIPT.row_rule("declared", SPLITS, day, row, h),
                    SCRIPT.rds.is_risk_date(SPLITS, row, h),
                    f"{day} h={h}",
                )

    def test_every_variant_keeps_every_declared_risk_date(self):
        for variant in SCRIPT.VARIANTS:
            for day, row in CASES.items():
                for h in (1, 2, 5):
                    if SCRIPT.rds.is_risk_date(SPLITS, row, h):
                        self.assertTrue(SCRIPT.row_rule(variant, SPLITS, day, row, h), f"{variant} {day} h={h}")

    def test_bill_days_add_a_bill_settlement_at_horizon_one_only(self):
        day, row = date(2019, 8, 13), CASES[date(2019, 8, 13)]
        self.assertFalse(SCRIPT.row_rule("declared", SPLITS, day, row, 1))
        self.assertTrue(SCRIPT.row_rule("bill_days", SPLITS, day, row, 1))
        self.assertFalse(SCRIPT.row_rule("bill_days", SPLITS, day, row, 2))

    def test_the_business_day_month_end_adds_the_second_last_business_day(self):
        day, row = date(2018, 12, 28), CASES[date(2018, 12, 28)]
        self.assertEqual(SPLITS.day_type(row), "ordinary")
        self.assertTrue(SCRIPT.row_rule("calendar_bd", SPLITS, day, row, 2))
        self.assertFalse(SCRIPT.row_rule("declared", SPLITS, day, row, 2))

    def test_only_the_wide_window_reaches_the_fourth_last_business_day_of_a_quarter(self):
        day, row = date(2019, 6, 25), CASES[date(2019, 6, 25)]
        self.assertFalse(SCRIPT.row_rule("calendar_bd", SPLITS, day, row, 2))
        self.assertTrue(SCRIPT.row_rule("calendar_wide", SPLITS, day, row, 2))

    def test_a_plain_day_is_a_risk_date_under_no_variant_at_horizon_two(self):
        day, row = date(2019, 2, 5), CASES[date(2019, 2, 5)]
        for variant in SCRIPT.VARIANTS:
            self.assertFalse(SCRIPT.row_rule(variant, SPLITS, day, row, 2), variant)


ANCHOR, BETWEEN = date(1999, 1, 1), date(1999, 1, 4)


def observation_of(day):
    """What the as-of rule hands a model at h = 1: dated at the anchor, carrying the scored day's columns."""

    SCRIPT.CALENDAR[day] = CASES[day]
    return DailyObservation(ANCHOR, CASES[day]), [ANCHOR, BETWEEN, day]


class DesignMembership(unittest.TestCase):
    def test_the_design_and_the_row_rule_agree(self):
        for variant in SCRIPT.VARIANTS:
            for day in CASES:
                observation, calendar = observation_of(day)
                design = SCRIPT.design_for(variant, FEATURES, SPLITS, calendar, 1)
                self.assertEqual(
                    design.member(observation), SCRIPT.row_rule(variant, SPLITS, day, CASES[day], 1), f"{variant} {day}"
                )

    def test_the_scored_day_is_read_from_the_calendar_not_from_the_anchor(self):
        # Dated at its anchor the observation is an ordinary Friday; the scored day, 2018-12-28, is the
        # second-last business day of the month.
        day = date(2018, 12, 28)
        observation, calendar = observation_of(day)
        design = SCRIPT.design_for("calendar_bd", FEATURES, SPLITS, calendar, 1)
        self.assertTrue(design.member(observation))

    def test_an_observation_of_another_day_is_refused(self):
        """Recorded mutation: `if float(observation.values[column]) != float(CALENDAR[day][column]):` in
        `design_for` replaced by `if False:` fails this test with `AssertionError: ValueError not raised`."""

        day = date(2019, 6, 25)
        observation, calendar = observation_of(day)
        SCRIPT.CALENDAR[day] = CASES[date(2019, 2, 5)]
        design = SCRIPT.design_for("calendar_bd", FEATURES, SPLITS, calendar, 1)
        with self.assertRaises(ValueError):
            design.member(observation)

    def test_without_the_settlement_inputs_the_design_reads_no_settlement(self):
        features = tuple(name for name in FEATURES if not name.startswith("treasury_settlement"))
        day = date(2019, 8, 13)
        observation, calendar = observation_of(day)
        design = SCRIPT.design_for("bill_days", features, SPLITS, calendar, 1)
        self.assertFalse(design.member(observation))


class OnsetLabelNeedsALabel(unittest.TestCase):
    def test_the_skew_t_quantile_has_no_onset_label(self):
        with self.assertRaises(ValueError):
            SCRIPT.variant_predictor("quantile_skewt", FEATURES, SPLITS, 61, "onset_label", [])


if __name__ == "__main__":
    unittest.main()
