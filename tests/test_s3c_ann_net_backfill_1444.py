"""`scripts/s3c_ann_net_backfill_1444.py` (#1444; H4 step 3 on the H5 candidate, development tier): (s3c-ann-net) trained on the admitted 2014-18 back-filled history.

Written first, against `metadata/s3c_ann_net_backfill_1444.json`. The study adds a two-stage refit (the settlement and market-holiday terms are fitted on
published-target pairs only, the other three on every pair), a term table that serves the back-filled rows, and the guards that keep the back-fill to training
history. The arithmetic and the guards are pinned here on hand cases; the walks themselves are #1288's and run in the script.

**Recorded mutations** (4 November 2026).

1. In `require_published_targets` (a pair whose target is a back-filled row must never enter the fit of the settlement and market-holiday terms: its blank
   settlement column would be read as "no settlement"), the line

       if pair.target < prefix:

   was changed to `if False:`. `PublishedTargetTests.test_a_back_filled_target_is_refused` then failed with `AssertionError: LookAheadError not raised`;
   restored, it passes.

2. In `require_backfill_guards` (every refit that trains on back-filled values must pass the posting instant and the admitted series, #572, #742, #1230), the
   line

       backfill.require_series_admitted([fold], reads, admitted, where=where)

   was changed to `pass`. `BackfillGuardTests.test_a_series_that_is_not_admitted_is_refused` then failed with `AssertionError: LookAheadError not raised`;
   restored, it passes.

3. In `require_instant` (the study is made at 18:00), the line `if decision_time != INSTANT_TIME:` was changed to `if False:`.
   `InstantTests.test_a_run_at_another_instant_is_refused` then failed with `AssertionError: ValueError not raised`; restored, it passes.
"""

from __future__ import annotations

import importlib.util
import sys
import unittest
from datetime import date, datetime, time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
_spec = importlib.util.spec_from_file_location("s3c_ann_net_backfill_1444", ROOT / "scripts" / "s3c_ann_net_backfill_1444.py")
script = importlib.util.module_from_spec(_spec)
sys.modules["s3c_ann_net_backfill_1444"] = script
_spec.loader.exec_module(script)

from repo_model import backfill, s3c_announced, spread_mr_calendar as cal, spread_mr_state_calendar as sc  # noqa: E402
from repo_model.data import DailyObservation  # noqa: E402
from repo_model.splits import LookAheadError  # noqa: E402

ARM = s3c_announced.ANN_NET_ARM
FLAGS = {name: 0 for name in cal.ALL_TERMS}


def pair(raw, target, *, quarter=0, coupon=0.0, scale=1.0):
    flags = dict(FLAGS, quarter_end=quarter, settlement_coupon=1 if coupon else 0)
    sizes = {"settlement_coupon": coupon, "settlement_bill": 0.0}
    return sc.StatePair(raw, scale, flags, 1.0, sizes, target - 1, target)


def many(n, start, **kw):
    return [pair(0.0, start + i, **kw) for i in range(n)]


class PartitionTests(unittest.TestCase):
    def test_the_terms_known_on_a_back_filled_row_are_the_three_calendar_columns(self):
        self.assertEqual(script.A_TERMS, ("quarter_end", "tax_date", "dom_19_23"))
        self.assertEqual(script.known_terms(ARM.location), ("quarter_end", "tax_date", "dom_19_23"))

    def test_the_four_others_are_the_settlement_and_market_holiday_terms(self):
        self.assertEqual(script.unknown_terms(ARM.location), ("month_end", "settlement_coupon", "settlement_bill", "post_month_end_window"))

    def test_the_two_groups_cover_the_arm(self):
        self.assertEqual(set(script.known_terms(ARM.location)) | set(script.unknown_terms(ARM.location)), set(ARM.location))


class PrefixFlagTests(unittest.TestCase):
    def test_a_back_filled_row_reads_its_own_calendar_columns(self):
        rows = [DailyObservation(date(2014, 9, 30), {"quarter_end": 1.0, "tax_date": 0.0}),
                DailyObservation(date(2014, 10, 1), {"quarter_end": 0.0, "tax_date": 0.0}),
                DailyObservation(date(2014, 10, 20), {"quarter_end": 0.0, "tax_date": 1.0})]
        flags = script.prefix_flags(rows, cal.ALL_TERMS)
        self.assertEqual(flags["quarter_end"], [1, 0, 0])
        self.assertEqual(flags["tax_date"], [0, 0, 1])
        self.assertEqual(flags["dom_19_23"], [0, 0, 1])

    def test_a_term_with_no_flag_on_a_back_filled_row_reads_zero(self):
        rows = [DailyObservation(date(2014, 9, 30), {})]
        flags = script.prefix_flags(rows, cal.ALL_TERMS)
        for name in ("month_end", "settlement_coupon", "settlement_bill", "post_month_end_window"):
            self.assertEqual(flags[name], [0])


class PublishedTargetTests(unittest.TestCase):
    def test_a_published_target_passes(self):
        script.require_published_targets(many(3, 10), 5, where="test")

    def test_a_back_filled_target_is_refused(self):
        with self.assertRaises(LookAheadError):
            script.require_published_targets(many(3, 3), 5, where="test")


class TwoStageTests(unittest.TestCase):
    def setUp(self):
        # 40 published pairs: three coupon-settlement days that lift the residual by 0.5 scale units, two quarter-end days, the rest ordinary
        self.pub = many(40, 20)
        self.pub[2] = pair(0.5, 22, coupon=1.0)
        self.pub[7] = pair(0.5, 27, coupon=1.0)
        self.pub[11] = pair(0.5, 31, coupon=1.0)
        self.pub[3] = pair(1.0, 23, quarter=1)
        self.pub[9] = pair(1.0, 29, quarter=1)
        # back-filled pairs: five quarter-end days that lift the residual by 1.0, no settlement column
        self.old = many(15, 0)
        for i in (1, 4, 6, 9, 12):
            self.old[i] = pair(1.0, i, quarter=1)

    def test_the_extra_quarter_ends_let_the_term_enter(self):
        published_only = script.two_stage(self.pub, 20, ARM, 1)
        extended = script.two_stage(self.old + self.pub, 20, ARM, 1)
        self.assertNotIn("quarter_end", published_only.effect)
        self.assertIn("quarter_end", extended.effect)
        self.assertEqual(extended.flagged["quarter_end"], 7)

    def test_the_settlement_effect_is_the_published_only_effect(self):
        alone = sc.fit_state_terms(
            self.pub, regressors=cal.regressors_of(ARM, 1), terms=ARM.location, interact=False, robust=True, training_pairs="direct",
            ridge=ARM.ridge, sized=True)
        extended = script.two_stage(self.old + self.pub, 20, ARM, 1)
        self.assertAlmostEqual(extended.effect["settlement_coupon"], alone.effect["settlement_coupon"], places=12)

    def test_a_back_filled_pair_does_not_move_the_settlement_effect(self):
        a = script.two_stage(self.old + self.pub, 20, ARM, 1)
        b = script.two_stage(many(30, -30) + self.old + self.pub, 20, ARM, 1)
        self.assertAlmostEqual(a.effect["settlement_coupon"], b.effect["settlement_coupon"], places=12)
        self.assertEqual(a.flagged["settlement_coupon"], 3)

    def test_the_estimate_counts_every_pair_and_keeps_the_arm_sized(self):
        extended = script.two_stage(self.old + self.pub, 20, ARM, 1)
        self.assertEqual(extended.pairs, len(self.old) + len(self.pub))
        self.assertTrue(extended.sized)
        self.assertEqual(len(extended.residuals), len(self.old) + len(self.pub))

    def test_without_back_filled_pairs_it_is_the_arm_as_it_is(self):
        alone = sc.fit_state_terms(
            self.pub, regressors=cal.regressors_of(ARM, 1), terms=ARM.location, interact=False, robust=True, training_pairs="direct",
            ridge=ARM.ridge, sized=True)
        same = script.two_stage(self.pub, 20, ARM, 1)
        self.assertEqual(set(same.effect), set(alone.effect))
        for name, value in alone.effect.items():
            self.assertAlmostEqual(same.effect[name], value, places=6)


class BackfillGuardTests(unittest.TestCase):
    ADMITTED = {"sofr": datetime(2018, 5, 17), "iorb": datetime(2018, 5, 17), "tgcr": datetime(2018, 5, 17), "bgcr": datetime(2018, 5, 17)}
    READS = ("iorb", "sofr")

    def dates(self):
        return [date(2014, 8, 22)] + [date.fromordinal(date(2018, 6, 1).toordinal() + i) for i in range(30)]

    def test_a_fit_after_the_posting_instant_with_admitted_series_passes(self):
        days = self.dates()
        script.require_backfill_guards(days, 20, days[25], datetime(2018, 5, 17), self.ADMITTED, self.READS, where="test")

    def test_a_fit_before_the_posting_instant_is_refused(self):
        days = [date(2014, 8, 22), date(2018, 5, 1), date(2018, 5, 2)]
        with self.assertRaises(LookAheadError):
            script.require_backfill_guards(days, 2, days[2], datetime(2018, 5, 17), self.ADMITTED, self.READS, where="test")

    def test_an_undeclared_posting_instant_is_refused(self):
        days = self.dates()
        with self.assertRaises(LookAheadError):
            script.require_backfill_guards(days, 20, days[25], None, self.ADMITTED, self.READS, where="test")

    def test_a_series_that_is_not_admitted_is_refused(self):
        days = self.dates()
        admitted = {k: v for k, v in self.ADMITTED.items() if k != "iorb"}
        with self.assertRaises(LookAheadError):
            script.require_backfill_guards(days, 20, days[25], datetime(2018, 5, 17), admitted, self.READS, where="test")

    def test_a_fit_on_published_rows_only_needs_no_back_filled_series(self):
        days = [date(2018, 6, 1), date(2018, 6, 4), date(2018, 6, 5)]
        script.require_backfill_guards(days, 2, days[2], None, {}, self.READS, where="test")


class BuildExtendedTests(unittest.TestCase):
    PUBLISHED = [{"date": "2018-04-03", "sofr": "1.83", "iorb": "1.75"}, {"date": "2018-04-04", "sofr": "1.74", "iorb": "1.75"},
                 {"date": "2026-01-02", "sofr": "3.7", "iorb": "3.65"}]

    def scratch(self, sofr="1.83"):
        return [{"date": "2018-03-29", "sofr": "1.8", "iorb": "1.75", "extra": "x"}, {"date": "2018-04-03", "sofr": sofr, "iorb": "1.75"}]

    def test_the_back_filled_rows_come_first_and_every_published_row_follows(self):
        rows = script.build_extended(self.scratch(), self.PUBLISHED, ("sofr", "iorb"))
        self.assertEqual([r["date"] for r in rows], ["2018-03-29", "2018-04-03", "2018-04-04", "2026-01-02"])
        self.assertEqual(set(rows[0]), set(self.PUBLISHED[0]))

    def test_a_published_day_that_differs_is_refused(self):
        with self.assertRaises(ValueError):
            script.build_extended(self.scratch("1.84"), self.PUBLISHED, ("sofr", "iorb"))


class BackFilledTurnDayTests(unittest.TestCase):
    DAYS = [date(2014, 9, 29), date(2014, 9, 30), date(2014, 10, 1), date(2014, 10, 2), date(2014, 10, 31), date(2014, 11, 3)]

    def test_a_month_before_the_holiday_table_reads_its_turn_days_from_the_panel_days(self):
        from repo_model import turn_days
        with script.back_filled_turn_days(self.DAYS):
            self.assertEqual(turn_days.turn_days_of_month(2014, 9), (date(2014, 9, 30), date(2014, 10, 1)))
            self.assertEqual(turn_days.turn_label(date(2014, 10, 1)), turn_days.QUARTER_END_TURN)
            self.assertIsNone(turn_days.turn_label(date(2014, 10, 2)))

    def test_a_month_the_table_covers_is_the_tables(self):
        from repo_model import turn_days
        before = turn_days.turn_days_of_month(2019, 3)
        with script.back_filled_turn_days(self.DAYS):
            self.assertEqual(turn_days.turn_days_of_month(2019, 3), before)

    def test_the_table_reading_is_restored(self):
        from repo_model import turn_days
        original = turn_days.turn_days_of_month
        with script.back_filled_turn_days(self.DAYS):
            pass
        self.assertIs(turn_days.turn_days_of_month, original)
        with self.assertRaises(ValueError):
            turn_days.turn_days_of_month(2014, 9)

    def test_a_month_before_the_panel_starts_has_no_turn_day_on_it(self):
        from repo_model import turn_days
        with script.back_filled_turn_days(self.DAYS):
            self.assertEqual(turn_days.turn_days_of_month(2014, 7), (date.min, date.min))

    def test_a_month_with_no_panel_day_is_refused(self):
        from repo_model import turn_days
        with script.back_filled_turn_days(self.DAYS):
            with self.assertRaises(ValueError):
                turn_days.turn_days_of_month(2014, 12)


class InstantTests(unittest.TestCase):
    def test_the_declared_instant_is_eighteen_hundred(self):
        self.assertEqual(script.INSTANT_TIME, time(18, 0))

    def test_the_run_at_the_declared_instant_passes(self):
        script.require_instant(time(18, 0))

    def test_a_run_at_another_instant_is_refused(self):
        with self.assertRaises(ValueError):
            script.require_instant(time(16, 0))


class ConsistencyTests(unittest.TestCase):
    def test_the_arm_must_refit_on_the_control_refit_days(self):
        script.require_same_refits([date(2018, 7, 19), date(2018, 8, 20)], [date(2018, 7, 19), date(2018, 8, 20)])
        with self.assertRaises(ValueError):
            script.require_same_refits([date(2018, 7, 19), date(2018, 8, 20)], [date(2018, 7, 19), date(2018, 8, 21)])

    def test_the_published_rows_of_the_extended_panel_must_be_the_published_panel(self):
        published = [DailyObservation(date(2018, 4, 3), {"sofr": 1.83, "iorb": 1.75, "quarter_end": 0.0})]
        ok = [DailyObservation(date(2018, 3, 29), {"sofr": 1.8, "iorb": 1.75, "quarter_end": 1.0})] + published
        script.require_same_published(published, ok, ("sofr", "iorb", "quarter_end"))
        bad = [ok[0], DailyObservation(date(2018, 4, 3), {"sofr": 1.84, "iorb": 1.75, "quarter_end": 0.0})]
        with self.assertRaises(ValueError):
            script.require_same_published(published, bad, ("sofr", "iorb", "quarter_end"))

    def test_the_extended_panel_must_be_back_filled_before_the_first_published_row(self):
        published = [DailyObservation(date(2018, 4, 3), {"sofr": 1.83})]
        with self.assertRaises(ValueError):
            script.require_same_published(published, published, ("sofr",))


class AlikeTests(unittest.TestCase):
    def test_scores_that_differ_by_rounding_are_alike(self):
        days = [date(2026, 1, 2), date(2026, 1, 5)]
        self.assertTrue(script.alike({days[0]: 1.0, days[1]: 2.0}, {days[0]: 1.0 + 1e-12, days[1]: 2.0 - 1e-12}, days))

    def test_scores_that_differ_are_not_alike(self):
        days = [date(2026, 1, 2), date(2026, 1, 5)]
        self.assertFalse(script.alike({days[0]: 1.0, days[1]: 2.0}, {days[0]: 1.0, days[1]: 2.001}, days))


class ReadingTests(unittest.TestCase):
    def test_a_gain_is_an_interval_wholly_on_the_side_of_the_arm(self):
        self.assertEqual(script.reading({"difference": 0.1, "difference_interval": [0.02, 0.2]}), "gain")

    def test_a_cost_is_an_interval_wholly_against_the_arm(self):
        self.assertEqual(script.reading({"difference": -0.1, "difference_interval": [-0.2, -0.02]}), "cost")

    def test_an_interval_that_covers_zero_is_undecided(self):
        self.assertEqual(script.reading({"difference": 0.1, "difference_interval": [-0.02, 0.2]}), "undecided")

    def test_an_identical_pair_is_identical(self):
        self.assertEqual(script.reading({"identical": True, "days": 9}), "identical")


if __name__ == "__main__":
    unittest.main()
