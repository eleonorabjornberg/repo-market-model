"""#1135, #1161: the month-end turn definition is one function, in force with `docs/decisions/month-end-turn.md`.

`turn_days.IN_FORCE` is the switch, and it is `True` exactly when the record sits in `docs/decisions/` (PR #1139 drafted it,
#1161 put it in force on her `GO #1135`). In force, `turn_days.reporting_day_type` (B2's pools, the mean-reversion
level, the day-type splits) and `risk_dates.is_risk_date(..., reporting_on=...)` read the turn labels of `turn_days`; with the
switch patched off they give the legacy reading, which the tests below keep. Nothing here reads a source, a publication
time or a revision: every label is a function of the date and the holiday table, so no leakage guard is added and no
mutation is recorded.
"""

import json
import unittest
from datetime import date
from pathlib import Path
from unittest import mock

from repo_model import risk_dates, risk_date_spread, turn_days as td
from repo_model.evaluation_splits import load_split_declaration

REPO = Path(__file__).resolve().parents[1]
SPLITS = load_split_declaration(REPO / "metadata" / "evaluation_splits.json")


def values(day, *, quarter_end=0.0, tax=0.0, to_end=10.0, coupons=0.0):
    return {
        "days_to_month_end": to_end,
        "quarter_end": quarter_end,
        "tax_date": tax,
        "treasury_settlement_coupons": coupons,
    }


def reporting(day, **kw):
    return td.reporting_day_type(SPLITS, day, values(day, **kw))


def on(flag=True):
    return mock.patch.object(td, "IN_FORCE", flag)


class TestInForceWithTheRecord(unittest.TestCase):
    def test_the_switch_is_on_and_the_record_is_in_decisions(self):
        self.assertTrue(td.IN_FORCE)
        self.assertTrue(td.in_force())
        self.assertTrue((REPO / "docs" / "decisions" / "month-end-turn.md").exists())
        self.assertFalse((REPO / "docs" / "decisions" / "drafts" / "month-end-turn.md").exists())

    def test_the_record_says_it_is_in_force_and_cites_her_go(self):
        record = (REPO / "docs" / "decisions" / "month-end-turn.md").read_text()
        self.assertIn("in force", record.split("\n\n")[0] + record.split("\n\n")[1])
        self.assertIn("GO #1135", record)
        self.assertNotIn("not in force", record)

    def test_the_switch_and_the_record_move_together(self):
        in_force = (REPO / "docs" / "decisions" / "month-end-turn.md").exists()
        self.assertEqual(td.IN_FORCE, in_force)

    def test_the_attestation_names_this_change(self):
        entries = json.loads((REPO / "metadata" / "owner_attestations.json").read_text())["attestations"]
        mine = [e for e in entries if e["issue"] == 1135 and e["comment_id"] == 6354007213 and "IN_FORCE True" in e["what"]]
        self.assertEqual(len(mine), 1)
        self.assertEqual(mine[0]["kind"], "decisions")

    def test_reporting_day_type_is_the_turn_label_by_default(self):
        self.assertEqual(reporting(date(2019, 5, 30), to_end=1.0), "ordinary")
        self.assertEqual(reporting(date(2019, 5, 31), to_end=0.0), "turn")
        self.assertEqual(reporting(date(2019, 6, 3), to_end=27.0), "turn")
        self.assertEqual(reporting(date(2019, 6, 28), quarter_end=1.0, to_end=0.0), "quarter_end_turn")

    def test_the_risk_date_reading_drops_the_penultimate_day(self):
        self.assertFalse(
            risk_dates.is_risk_date(
                values(date(2019, 5, 30)), risk_dates.NON_ORDINARY, splits=SPLITS, coupon_clause=False,
                reporting_on=date(2019, 5, 30),
            )
        )


class TestB2ReadsTheTurnLabels(unittest.TestCase):
    def test_b2_for_a_year_end_target_is_the_trailing_years_year_end_spreads(self):
        """`protocol_benchmarks.b2_forecast` pools by `turn_days.reporting_day_type`, so a year-end target reads year-end rows.

        Run on the simulated panel of `benchmark_simulation` (spreads vary by row); the decision is 30 December 2019 and the
        target 31 December, whose window holds 31 December 2018 and 2 January 2019 only (the pool a fallback, #1155, would
        widen; B2 itself has none in force).
        """

        import benchmark_simulation as sim
        from repo_model import protocol_benchmarks as pb

        rows = sim.simulate(sim.ProcessSpec(), seed=741).rows
        days = [r.date for r in rows]
        t = days.index(date(2019, 12, 30))
        got = pb.b2_forecast(rows, t, registry=sim.REGISTRY, decision_time=sim.DECISION, splits=sim.SPLITS)
        window = [
            r.spread_bps for r in rows[:t]
            if date(2018, 12, 30) <= r.date and td.reporting_day_type(sim.SPLITS, r.date, r.values) == "year_end"
        ]
        self.assertEqual(len(window), 2)
        self.assertEqual(got[1], pb.empirical_quantiles(sorted(window)))


class TestTheLegacyReadingIsStillThereWhenSwitchedOff(unittest.TestCase):
    def test_reporting_day_type_is_the_old_month_end_label(self):
        with on(False):
            self.assertEqual(reporting(date(2019, 5, 30), to_end=1.0), "month_end")  # penultimate
            self.assertEqual(reporting(date(2019, 5, 31), to_end=0.0), "month_end")
            self.assertEqual(reporting(date(2019, 6, 3), to_end=27.0), "ordinary")
            self.assertEqual(reporting(date(2019, 6, 28), quarter_end=1.0, to_end=0.0), "quarter_end")


class TestTheDefinitionInForce(unittest.TestCase):
    def test_the_turn_is_the_last_business_day_and_the_first_of_the_next_month(self):
        with on():
            self.assertEqual(reporting(date(2019, 5, 31), to_end=0.0), "turn")
            self.assertEqual(reporting(date(2019, 6, 3), to_end=27.0), "turn")

    def test_the_penultimate_day_and_the_second_day_after_are_ordinary(self):
        with on():
            self.assertEqual(reporting(date(2019, 5, 30), to_end=1.0), "ordinary")
            self.assertEqual(reporting(date(2019, 6, 4), to_end=26.0), "ordinary")

    def test_a_quarter_end_adds_the_first_day_after_and_a_year_end_is_its_own_type(self):
        with on():
            self.assertEqual(reporting(date(2019, 6, 28), quarter_end=1.0, to_end=0.0), "quarter_end_turn")
            self.assertEqual(reporting(date(2019, 7, 1), to_end=30.0), "quarter_end_turn")
            self.assertEqual(reporting(date(2018, 12, 31), quarter_end=1.0, to_end=0.0), "year_end")
            self.assertEqual(reporting(date(2019, 1, 2), to_end=29.0), "year_end")

    def test_a_holiday_rolls_the_turn(self):
        with on():
            # 2019-08-31 was a Saturday, 2019-09-02 Labor Day
            self.assertEqual(reporting(date(2019, 8, 30), to_end=1.0), "turn")
            self.assertEqual(reporting(date(2019, 9, 3), to_end=27.0), "turn")
            self.assertEqual(reporting(date(2019, 9, 2), to_end=28.0), "ordinary")

    def test_a_tax_date_outside_the_turn_keeps_its_type(self):
        with on():
            self.assertEqual(reporting(date(2019, 9, 16), tax=1.0, to_end=14.0), "tax_date")
            self.assertEqual(reporting(date(2019, 5, 31), tax=1.0, to_end=0.0), "turn")

    def test_a_hole_in_a_calendar_column_is_still_a_data_error(self):
        row = values(date(2019, 5, 31))
        row["tax_date"] = None
        with on(), self.assertRaises(ValueError):
            td.reporting_day_type(SPLITS, date(2019, 5, 31), row)

    def test_the_risk_date_set_follows_the_label(self):
        def risk(day, **kw):
            return risk_dates.is_risk_date(
                values(day, **kw), risk_dates.NON_ORDINARY, splits=SPLITS, coupon_clause=False, reporting_on=day
            )

        with on():
            self.assertFalse(risk(date(2019, 5, 30), to_end=1.0))
            self.assertTrue(risk(date(2019, 5, 31), to_end=0.0))
            self.assertTrue(risk(date(2019, 6, 3), to_end=27.0))

    def test_h6_names_the_turn_types_instead_of_calling_them_settlement(self):
        with on():
            self.assertEqual(
                risk_date_spread.risk_day_type(date(2019, 5, 31), values(date(2019, 5, 31), to_end=0.0), SPLITS), "turn"
            )
            self.assertEqual(
                risk_date_spread.risk_day_type(
                    date(2019, 7, 1), values(date(2019, 7, 1), to_end=30.0), SPLITS
                ),
                "quarter_end_turn",
            )

    def test_b2_pools_by_the_label(self):
        # `b2_forecast` groups by `splits.reporting_day_type`, so the pool of a turn day holds turn days only
        with on():
            kinds = {d: reporting(d, to_end=t) for d, t in ((date(2019, 5, 30), 1.0), (date(2019, 5, 31), 0.0))}
        self.assertEqual(kinds, {date(2019, 5, 30): "ordinary", date(2019, 5, 31): "turn"})


class TestTheDeclaredSplitIsUntouched(unittest.TestCase):
    def test_the_frozen_split_declaration_still_reads_the_legacy_month_end_even_when_the_record_is_on(self):
        # evaluation_splits.SplitDeclaration is in the live scorer's frozen declaration; the new reading never edits it
        with on():
            self.assertEqual(SPLITS.reporting_day_type(date(2019, 5, 30), values(date(2019, 5, 30), to_end=1.0)), "month_end")

    def test_a_substitute_split_object_keeps_its_own_reading_when_the_record_is_on(self):
        class Own:
            def reporting_day_type(self, when, row):
                return "own"

        with on():
            self.assertEqual(td.reporting_day_type(Own(), date(2019, 5, 31), values(date(2019, 5, 31))), "own")


class TestTheDaySetsThatMove(unittest.TestCase):
    def test_the_day_sets_function_counts_what_moves(self):
        moved = td.day_set_changes(date(2019, 1, 1), date(2019, 12, 31), splits=SPLITS)
        self.assertIn(date(2019, 5, 30), moved["leave_month_end"])
        self.assertIn(date(2019, 6, 3), moved["join_turn"])
        self.assertNotIn(date(2019, 5, 31), moved["leave_month_end"])
        self.assertNotIn(date(2019, 5, 31), moved["join_turn"])
        self.assertIn(date(2019, 1, 2), moved["join_turn"])  # first business day of 2019: year-end type


if __name__ == "__main__":
    unittest.main()
