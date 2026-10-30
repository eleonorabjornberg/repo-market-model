"""Calendar and FOMC effects as additive terms on scaled mean reversion (#1115; H5 step 3, development tier).

`metadata/calendar_mr_1115.json` is the declaration; `repo_model.spread_mr_calendar` is its arithmetic. What these tests pin: the
ridge solver on hand cases; the term flags on known days; that each term is read from the *target* row at every lead and that a
scheduled field is unreadable where the as-of rule refuses it (a settlement at lead 2 or more, the IORB window's day of change
at lead 2 or more); that an announcement made after the decision instant moves no flag; that a one-step fit of the terms'
columns is refused by `one_step_guard` while the direct fit needs no allow-list entry; the planted location and scale effects;
and that the arm with no term reproduces #941's variant.

Recorded mutations (each applied to the tree, the named test run, and reverted):

* `readable_offsets`: `j >= lead - 1` replaced with `j >= lead - 2`, so a scheduled field of the day before the decision is
  read. `test_a_scheduled_term_is_readable_only_where_the_as_of_rule_admits_it` failed with `AssertionError` (settlement_coupon
  was readable at lead 2, where `InformationRule` raises `LookAheadError`); `test_a_scheduled_row_after_the_decision_is_refused`
  is untouched by it (it calls `require_public` directly).
* `target_row`: `decision_index + lead` replaced with `decision_index + lead - 1`, so every term is read one row off the
  target (the #914 class). `test_every_term_is_read_from_the_target_row_at_every_lead` failed with `AssertionError`.
* `fit_calendar_terms`: delete the `@guard_one_step_fit` line. `test_a_one_step_fit_of_a_term_column_is_refused_by_the_guard`
  failed with `AssertionError` (the `ValueError` raised was the function's own "direct pairs only", not the guard's message
  naming the column); restored, it passes.
"""

from __future__ import annotations

import dataclasses
import unittest
from datetime import date, datetime, time
from pathlib import Path

from repo_model.decision_instant import DECISION_TIME
from repo_model import announced_iorb, asof, contract
from repo_model import one_step_guard as osg
from repo_model import spread_mean_reversion as smr
from repo_model import spread_mr_calendar as cal
from repo_model import spread_mr_fhs as fhs
from repo_model.splits import LookAheadError

import test_protocol_benchmarks as tpb

ROOT = Path(__file__).resolve().parent.parent
TABLE = ROOT / "tests" / "fixtures" / "snapshots" / "fed-iorb-announcements" / "iorb_changes.csv"
DECISION = DECISION_TIME  # the scheduled IORB-change features are declared at the decision instant (18:00 since #1312)
PANEL = tpb.published_panel()["rows"]
ANNOUNCEMENTS = announced_iorb.load_announcements(TABLE)
TABLE_ALL = cal.TermTable(PANEL, ANNOUNCEMENTS)
SETTINGS = dict(registry=tpb.REGISTRY, decision_time=tpb.DECISION, splits=tpb.SPLITS)


def index_of(day: str) -> int:
    return next(i for i, row in enumerate(PANEL) if row.date.isoformat() == day)


class SolverTests(unittest.TestCase):

    def test_an_exact_line_is_recovered_without_a_penalty(self):
        rows = [[1.0, 0.0], [1.0, 1.0], [1.0, 0.0], [1.0, 1.0]]
        out = cal.solve_ridge(rows, [2.0, 5.0, 2.0, 5.0], 0.0)
        self.assertAlmostEqual(out[0], 2.0)
        self.assertAlmostEqual(out[1], 3.0)

    def test_the_penalty_shrinks_a_term_and_never_the_intercept(self):
        rows = [[1.0, 0.0], [1.0, 0.0], [1.0, 1.0], [1.0, 1.0], [1.0, 1.0]]
        y = [2.0, 2.0, 5.0, 5.0, 5.0]
        out = cal.solve_ridge(rows, y, 1.0)
        # intercept 2 + b*0 for the unflagged, 3 flagged: normal equations give b = 3 * 3 / (3 + 1) after centring at the intercept
        self.assertLess(out[1], 3.0)
        self.assertGreater(out[1], 1.0)
        self.assertAlmostEqual(sum(out[0] + out[1] * r[1] for r in rows) / 5, sum(y) / 5)  # residuals sum to zero

    def test_an_empty_design_or_a_singular_one_is_refused(self):
        with self.assertRaises(ValueError):
            cal.solve_ridge([], [], 1.0)
        with self.assertRaises(ValueError):
            cal.solve_ridge([[0.0], [0.0]], [1.0, 2.0], 0.0)


class FlagTests(unittest.TestCase):

    def flag(self, term, lead, day):
        return TABLE_ALL.flag(term, lead, index_of(day))

    def test_known_days_carry_their_flags(self):
        self.assertEqual(self.flag("quarter_end", 1, "2024-06-28"), 1)
        self.assertEqual(self.flag("quarter_end", 3, "2024-06-27"), 0)
        self.assertEqual(self.flag("month_end", 1, "2024-05-31"), 1)
        self.assertEqual(self.flag("month_end", 1, "2024-05-15"), 0)
        self.assertEqual(self.flag("dom_19_23", 2, "2024-06-21"), 1)
        self.assertEqual(self.flag("dom_19_23", 2, "2024-06-24"), 0)
        self.assertEqual(self.flag("post_month_end_window", 5, "2024-06-05"), 1)  # third market day of June 2024
        self.assertEqual(self.flag("post_month_end_window", 5, "2024-06-06"), 0)
        self.assertEqual(self.flag("fomc_day", 2, "2024-06-12"), 1)  # the June 2024 meeting
        self.assertEqual(self.flag("fomc_day", 2, "2024-06-13"), 0)

    def test_the_iorb_window_is_the_day_of_the_change_and_the_two_after_it_where_readable(self):
        # the IORB cut of 2024-09-19 took effect on 2024-09-19; 9/19, 9/20 and 9/23 are the window at lead 1
        for day, expected in (("2024-09-18", 0), ("2024-09-19", 1), ("2024-09-20", 1), ("2024-09-23", 1), ("2024-09-24", 0)):
            with self.subTest(day=day):
                self.assertEqual(self.flag("iorb_window", 1, day), expected, day)
        # at lead 2 the day of the change is not readable (announced the day before the row at the earliest): 9/19 is 0
        self.assertEqual(self.flag("iorb_window", 2, "2024-09-19"), 0)
        self.assertEqual(self.flag("iorb_window", 2, "2024-09-23"), 1)
        self.assertEqual(self.flag("iorb_window", 3, "2024-09-20"), 0)
        self.assertEqual(self.flag("iorb_window", 3, "2024-09-23"), 1)
        self.assertIsNone(self.flag("iorb_window", 4, "2024-09-23"))

    def test_a_settlement_is_a_lead_one_term_only(self):
        day = next(row.date for row in PANEL if row.values.get("treasury_settlement_coupons") and row.date.year == 2024)
        self.assertEqual(TABLE_ALL.flag("settlement_coupon", 1, index_of(day.isoformat())), 1)
        for lead in (2, 3, 4, 5):
            self.assertIsNone(TABLE_ALL.flag("settlement_coupon", lead, index_of(day.isoformat())))


class AvailabilityTests(unittest.TestCase):

    def test_a_scheduled_term_is_readable_only_where_the_as_of_rule_admits_it(self):
        dates = [row.date for row in PANEL]
        probe = index_of("2024-06-05")
        for term in cal.TERMS:
            for lead in (1, 2, 3, 4, 5):
                for j in term.span:
                    columns = tuple(c for c in term.reads if c in contract.FEATURE_FIELDS or c == "iorb_announced_change_bps")
                    if not term.scheduled or not columns:
                        continue
                    row = probe - j
                    horizon = lead - j  # the decision is `lead` rows before the target, so `horizon` rows before row `row`
                    admitted = horizon <= 0 or self.rule_admits(columns, dates, row, horizon)
                    with self.subTest(term=term.name, lead=lead, offset=j):
                        self.assertEqual(j in cal.readable_offsets(term, lead), admitted)

    @staticmethod
    def rule_admits(columns, dates, row, horizon) -> bool:
        rule = asof.InformationRule(tpb.REGISTRY, columns, decision_time=DECISION, horizon=horizon)
        try:
            rule.check(dates, rule.information_set(dates, row))
        except LookAheadError:
            return False
        return True

    def test_the_declared_leads_of_each_term(self):
        by_term = {t.name: [lead for lead in range(1, 6) if cal.available(t, lead)] for t in cal.TERMS}
        self.assertEqual(by_term["settlement_coupon"], [1])
        self.assertEqual(by_term["settlement_bill"], [1])
        self.assertEqual(by_term["iorb_window"], [1, 2, 3])
        for name in ("month_end", "quarter_end", "tax_date", "dom_19_23", "fomc_day", "post_month_end_window"):
            self.assertEqual(by_term[name], [1, 2, 3, 4, 5], name)

    def test_a_scheduled_row_after_the_decision_is_refused(self):
        dates = [row.date for row in PANEL]
        di = index_of("2024-06-05")
        cal.require_public(cal.TERM["settlement_coupon"], [di + 1], di, dates)  # public at 15:00 on the decision day
        with self.assertRaises(LookAheadError):
            cal.require_public(cal.TERM["settlement_coupon"], [di + 2], di, dates)
        cal.require_public(cal.TERM["quarter_end"], [di + 5], di, dates)  # a calendar column is known whenever it is read


class TargetRowTests(unittest.TestCase):

    def test_every_term_is_read_from_the_target_row_at_every_lead(self):
        di = index_of("2024-06-05")
        for lead in (1, 2, 3, 4, 5):
            read = TABLE_ALL.read(lead, di)
            self.assertEqual(set(read), {t.name for t in cal.TERMS if cal.available(t, lead)})
            for name, value in read.items():
                self.assertEqual(value, TABLE_ALL.flag(name, lead, di + lead), (name, lead))
        # the June 2024 meeting is 11-12 June: the targets of leads 4 and 5 from 2024-06-05; lead 3's target (10 June) is not
        self.assertEqual(TABLE_ALL.read(5, di)["fomc_day"], 1)
        self.assertEqual(TABLE_ALL.read(4, di)["fomc_day"], 1)
        self.assertEqual(TABLE_ALL.read(3, di)["fomc_day"], 0)
        # 2024-06-07 is the target of lead 2 and 2024-06-06 of lead 1: the post-month-end window has ended
        self.assertEqual(cal.target_row(di, 3), di + 3)

    def test_an_announcement_made_after_the_decision_moves_no_flag(self):
        di = index_of("2024-09-17")
        cut = [a for a in ANNOUNCEMENTS if a.effective == date(2024, 9, 19)][0]
        self.assertEqual(cut.announced_at, datetime(2024, 9, 18, 14, 0))
        without = tuple(a for a in ANNOUNCEMENTS if a is not cut)
        other = cal.TermTable(PANEL, without)
        for lead in (1, 2, 3):
            self.assertEqual(TABLE_ALL.read(lead, di), other.read(lead, di), lead)  # announced after the 17 September decision
        di = index_of("2024-09-18")  # the decision is after the announcement: lead 1 reads the change
        self.assertEqual(TABLE_ALL.read(1, di)["iorb_window"], 1)
        self.assertEqual(other.read(1, di)["iorb_window"], 0)


class GuardTests(unittest.TestCase):

    def pairs(self):
        return [cal.PairRow(0.0, 1.0, {n: 0 for n in cal.ALL_TERMS}) for _ in range(5)]

    def test_a_one_step_fit_of_a_term_column_is_refused_by_the_guard(self):
        for term in cal.TERMS:
            if not term.reads:
                continue
            with self.subTest(term=term.name):
                with self.assertRaisesRegex(ValueError, r"one-step pairs.*served from the scored row"):
                    cal.fit_calendar_terms(
                        self.pairs(), regressors=term.reads, location=(term.name,), scale_terms=(), training_pairs="one_step"
                    )

    def test_the_direct_fit_is_admitted_with_no_allow_list_entry(self):
        for arm in cal.ARMS:
            for lead in (1, 2, 5):
                with self.assertRaises(ValueError):  # the same columns on a one-step fit are refused, so the guard is live here
                    osg.check_one_step_regressors("fit_calendar_terms", cal.regressors_of(arm, lead) + ("quarter_end",))
        self.assertFalse([k for k, v in osg.ONE_STEP_ALLOW_LIST.items() if v.fitter == "fit_calendar_terms"])
        estimate = cal.fit_calendar_terms(
            self.pairs(), regressors=("quarter_end",), location=("quarter_end",), scale_terms=(), training_pairs="direct"
        )
        self.assertEqual(estimate.pairs, 5)

    def test_a_training_pairing_other_than_direct_is_refused_even_without_a_column(self):
        with self.assertRaisesRegex(ValueError, "direct pairs only"):
            cal.fit_calendar_terms(self.pairs(), regressors=(), location=("dom_19_23",), scale_terms=(), training_pairs="one_step")


class EstimationTests(unittest.TestCase):

    def pairs(self, flagged=10, effect=3.0, widen=1.0):
        out = []
        for i in range(60):
            flags = {n: 0 for n in cal.ALL_TERMS}
            flags["quarter_end"] = 1 if i < flagged else 0
            noise = (-1.0) ** i * (1.0 + (i % 3) * 0.5)
            raw = noise * (widen if flags["quarter_end"] else 1.0) + (effect if flags["quarter_end"] else 0.0)
            out.append(cal.PairRow(raw, 1.0, flags))
        return out

    def fit(self, pairs, location=("quarter_end",), scale=()):
        return cal.fit_calendar_terms(pairs, regressors=("quarter_end",), location=location, scale_terms=scale, training_pairs="direct")

    def test_a_planted_location_effect_is_estimated_and_shifts_only_the_flagged_day(self):
        estimate = self.fit(self.pairs())
        self.assertAlmostEqual(estimate.effect["quarter_end"], 3.0, delta=0.5)
        flags = {n: 0 for n in cal.ALL_TERMS}
        plain = cal.lead_quantiles(estimate, centre=10.0, scale=1.0, flags=flags)
        flags["quarter_end"] = 1
        shifted = cal.lead_quantiles(estimate, centre=10.0, scale=1.0, flags=flags)
        for a, b in zip(plain, shifted):
            self.assertAlmostEqual(b - a, estimate.effect["quarter_end"])
        self.assertEqual(plain, sorted(plain))

    def test_a_term_with_too_few_flagged_pairs_is_absent(self):
        estimate = self.fit(self.pairs(flagged=cal.MIN_FLAGGED - 1))
        self.assertEqual(estimate.effect, {})
        self.assertEqual(estimate.flagged["quarter_end"], cal.MIN_FLAGGED - 1)

    def test_with_no_term_the_pool_is_the_scaled_residual_pool(self):
        pairs = self.pairs(effect=0.0)
        estimate = self.fit(pairs, location=())
        self.assertEqual(estimate.pool, cal.pb.empirical_quantiles(sorted(p.raw / p.scale for p in pairs)))

    def test_a_planted_scale_effect_widens_only_the_flagged_day(self):
        estimate = self.fit(self.pairs(effect=0.0, widen=3.0), location=(), scale=("quarter_end",))
        self.assertGreater(estimate.uplift["quarter_end"], 1.0)
        flags = {n: 0 for n in cal.ALL_TERMS}
        plain = cal.lead_quantiles(estimate, centre=0.0, scale=1.0, flags=flags)
        flags["quarter_end"] = 1
        wide = cal.lead_quantiles(estimate, centre=0.0, scale=1.0, flags=flags)
        self.assertGreater(wide[-1] - wide[0], 2.0 * (plain[-1] - plain[0]))
        self.assertEqual(wide, sorted(wide))

    def test_the_multiplier_is_floored(self):
        estimate = dataclasses.replace(self.fit(self.pairs()), uplift={"quarter_end": -5.0})
        self.assertEqual(cal.multiplier(estimate, {"quarter_end": 1}), cal.M_MIN)


class WalkTests(unittest.TestCase):

    DAYS = [row.date for row in PANEL if date(2024, 6, 3) <= row.date <= date(2024, 6, 14)]

    @classmethod
    def setUpClass(cls):
        cls.walk = cal.walk(PANEL, cls.DAYS, TABLE_ALL, **SETTINGS)

    def test_arm_a_is_941s_variant_exactly(self):
        reference = fhs.walk(PANEL, self.DAYS, [fhs.VARIANTS[0]], **SETTINGS)
        self.assertEqual(self.walk.forecasts[cal.ARM_A], reference.forecasts[fhs.VARIANTS[0].name])

    def test_every_arm_has_23_ordered_quantiles_at_every_lead_on_the_same_days(self):
        days = set(self.walk.forecasts[cal.ARM_A])
        self.assertTrue(days)
        for name in cal.ARM_NAMES:
            self.assertEqual(set(self.walk.forecasts[name]), days)
            for leads in self.walk.forecasts[name].values():
                for q in leads.values():
                    self.assertEqual(len(q), 23)
                    self.assertEqual(q, sorted(q))

    def test_the_fit_is_renewed_every_21_decision_days_with_the_base_model(self):
        self.assertEqual(len(self.walk.fits), 1)
        self.assertEqual(set(self.walk.estimates), set(self.walk.fits))

    def test_a_future_spread_moves_no_forecast(self):
        di = index_of("2024-06-07")
        panel = list(PANEL)
        for i in range(di + 1, len(panel)):
            values = dict(panel[i].values)
            values["sofr"] = float(values["iorb"]) + 40.0
            panel[i] = dataclasses.replace(panel[i], values=values)
        other = cal.walk(panel, [PANEL[di].date], TABLE_ALL, **SETTINGS)
        base = cal.walk(PANEL, [PANEL[di].date], TABLE_ALL, **SETTINGS)
        self.assertEqual(other.forecasts, base.forecasts)

    def test_the_one_step_walk_is_refused(self):
        with self.assertRaisesRegex(ValueError, "one-step pairs"):
            cal.walk(PANEL, self.DAYS[:2], TABLE_ALL, **SETTINGS, training_pairs="one_step")


if __name__ == "__main__":
    unittest.main()
