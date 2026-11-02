"""(s3c-gse): the GSE cash cycle as a ramp from the 19th to the 25th in place of the flat 19th-23rd term (#1274; H5 step 3, development tier).

`repo_model.s3c_gse` is (s3)'s term table with one column replaced: the slot of `dom_19_23` holds `ramp(date)`, 0 before the 19th and after
the 25th, `(d - 18) / 7` from the 19th to the 25th, read from the target row's own date. What these tests pin: the ramp on hand dates (the
first and last day, the middle, the days just outside, a weekend and a holiday inside the span); that every other term, at every lead and
row, is the base table's; that the column is read from the target row, at every lead, and that a forecast moves with the ramp of its own
target by exactly the fitted effect times the scale times the change; that the arm is (s3), unchanged, on the new table (terms, Huber, ridge
5, direct pairs); that a term of fractional values fits, and is recovered; that a one-step fit is still refused by the guard with no
allow-list entry; that a future spread or a future target date's ramp moves no forecast before it is read.

Recorded mutations (each applied to the tree, the named test run, and reverted):

* `ramp`: `(d - (FIRST_DAY - 1)) / _STEPS` replaced with `(d - FIRST_DAY) / _STEPS`, so the ramp starts at 0 on the 19th and ends at 6/7.
  `RampTests.test_the_ramp_on_hand_dates` failed with `AssertionError` (1/7 expected for 2025-03-19); restored, it passes.
* `GseTermTable.__init__`: `column = [ramp(day) for day in self.dates]` replaced with `[ramp(self.dates[max(i - 1, 0)]) for i, _ in enumerate(self.dates)]`,
  so each row carries the ramp of the row before it (the #914 class: a calendar column served one row off).
  `TableTests.test_the_ramp_is_read_from_the_target_row_at_every_lead` failed with `AssertionError`.
* `GseTermTable.__init__`: the `for lead in HORIZONS:` loop changed to write the column at lead 1 only. `TableTests.test_the_ramp_is_the_same_at_every_lead`
  failed with `AssertionError` (the flag at lead 2 was still the flat 19th-23rd flag).
"""

from __future__ import annotations

import unittest
from datetime import date
from pathlib import Path

from repo_model import announced_iorb
from repo_model import one_step_guard as osg
from repo_model import s3c_gse as gse
from repo_model import spread_mr_calendar as cal
from repo_model import spread_mr_state_calendar as sc
from repo_model.scoring_protocol import HORIZONS

import test_protocol_benchmarks as tpb

ROOT = Path(__file__).resolve().parent.parent
TABLE = ROOT / "tests" / "fixtures" / "snapshots" / "fed-iorb-announcements" / "iorb_changes.csv"
PANEL = tpb.published_panel()["rows"]
ANNOUNCEMENTS = announced_iorb.load_announcements(TABLE)
BASE = cal.TermTable(PANEL, ANNOUNCEMENTS)
GSE = gse.GseTermTable(PANEL, ANNOUNCEMENTS)
SETTINGS = dict(registry=tpb.REGISTRY, decision_time=tpb.DECISION, splits=tpb.SPLITS)
DATES = [row.date for row in PANEL]
S3 = sc.ARMS[2]


def index_of(day: str) -> int:
    return next(i for i, row in enumerate(PANEL) if row.date.isoformat() == day)


class RampTests(unittest.TestCase):

    def test_the_ramp_on_hand_dates(self):
        cases = {
            date(2025, 3, 18): 0.0, date(2025, 3, 19): 1 / 7, date(2025, 3, 20): 2 / 7, date(2025, 3, 22): 4 / 7,
            date(2025, 3, 24): 6 / 7, date(2025, 3, 25): 1.0, date(2025, 3, 26): 0.0, date(2025, 3, 1): 0.0, date(2025, 3, 31): 0.0,
            date(2024, 2, 29): 0.0, date(2025, 12, 25): 1.0,
        }
        for day, value in cases.items():
            self.assertAlmostEqual(gse.ramp(day), value, msg=str(day))

    def test_the_ramp_rises_in_equal_steps_from_the_19th_to_the_25th_and_is_zero_elsewhere(self):
        values = [gse.ramp(date(2025, 4, d)) for d in range(1, 31)]
        inside = values[gse.FIRST_DAY - 1 : gse.LAST_DAY]
        self.assertEqual(len(inside), 7)
        self.assertAlmostEqual(inside[-1], 1.0)
        for a, b in zip(inside, inside[1:]):
            self.assertAlmostEqual(b - a, 1 / 7)
        self.assertEqual([v for i, v in enumerate(values) if not gse.FIRST_DAY - 1 <= i < gse.LAST_DAY], [0.0] * 23)

    def test_a_weekend_or_holiday_day_is_not_renumbered(self):
        # 25 October 2025 is a Saturday and 19 October a Sunday: the panel rows that remain keep their own date's value
        self.assertEqual(date(2025, 10, 25).weekday(), 5)
        self.assertEqual(date(2025, 10, 19).weekday(), 6)
        self.assertAlmostEqual(gse.ramp(date(2025, 10, 20)), 2 / 7)
        self.assertAlmostEqual(gse.ramp(date(2025, 10, 24)), 6 / 7)
        self.assertEqual(gse.ramp(date(2025, 10, 27)), 0.0)
        # 19 June is a holiday: the 18th is outside, the 20th keeps 2/7
        self.assertAlmostEqual(gse.ramp(date(2024, 6, 20)), 2 / 7)

    def test_the_declared_shape(self):
        self.assertEqual((gse.FIRST_DAY, gse.LAST_DAY, gse.REPLACED_TERM), (19, 25, "dom_19_23"))


class TableTests(unittest.TestCase):

    def test_the_ramp_is_read_from_the_target_row_at_every_lead(self):
        for lead in HORIZONS:
            for di in range(40, len(PANEL) - 6, 7):
                read = GSE.read(lead, di)["dom_19_23"]
                self.assertEqual(read, gse.ramp(DATES[di + lead]), (lead, DATES[di]))
        for lead in HORIZONS:
            row = index_of("2024-06-24")
            self.assertEqual(GSE.flag("dom_19_23", lead, row), gse.ramp(date(2024, 6, 24)))
            self.assertNotEqual(GSE.flag("dom_19_23", lead, index_of("2024-06-26")), gse.ramp(date(2024, 6, 24)))

    def test_the_ramp_is_the_same_at_every_lead(self):
        for row in range(len(PANEL)):
            self.assertEqual({GSE.flag("dom_19_23", lead, row) for lead in HORIZONS}, {gse.ramp(DATES[row])})

    def test_every_other_term_is_the_base_tables_at_every_lead_and_row(self):
        for term in cal.TERMS:
            if term.name == gse.REPLACED_TERM:
                continue
            for lead in HORIZONS:
                self.assertEqual([GSE.flag(term.name, lead, r) for r in range(len(PANEL))],
                                 [BASE.flag(term.name, lead, r) for r in range(len(PANEL))], (term.name, lead))

    def test_the_replaced_slot_differs_from_the_flat_flag_only_where_the_ramp_does(self):
        for r in range(len(PANEL)):
            flat, ramped = BASE.flag("dom_19_23", 1, r), GSE.flag("dom_19_23", 1, r)
            self.assertEqual(flat, 1 if 19 <= DATES[r].day <= 23 else 0)
            if DATES[r].day < 19 or DATES[r].day > 25:
                self.assertEqual((flat, ramped), (0, 0))
            else:
                self.assertGreater(ramped, 0.0)

    def test_the_set_of_terms_is_unchanged(self):
        self.assertEqual([t.name for t in cal.TERMS], list(cal.ALL_TERMS))
        self.assertEqual(GSE.dates, BASE.dates)
        for lead in HORIZONS:
            self.assertEqual(GSE.flags_at(lead, 100).keys(), BASE.flags_at(lead, 100).keys())


def planted(effect: float, *, n: int = 60):
    """Pairs whose raw residual (scale 1) is `effect` times the ramp, with the ramp running through 0, 1/7 ... 1."""

    levels = [0.0, 1 / 7, 2 / 7, 3 / 7, 4 / 7, 5 / 7, 6 / 7, 1.0]
    pairs = []
    for i in range(n):
        value = levels[i % len(levels)]
        flags = {name: 0 for name in cal.ALL_TERMS}
        flags["dom_19_23"] = value
        pairs.append(sc.StatePair(effect * value, 1.0, flags, None))
    return pairs


class FitTests(unittest.TestCase):

    def fit(self, pairs, **kw):
        return sc.fit_state_terms(pairs, regressors=(), terms=("dom_19_23",), interact=False, robust=False, training_pairs="direct", ridge=0.0, **kw)

    def test_a_planted_ramp_effect_is_recovered_with_no_penalty(self):
        estimate = self.fit(planted(effect=2.5))
        self.assertAlmostEqual(estimate.effect["dom_19_23"], 2.5)
        self.assertEqual(estimate.terms, ("dom_19_23",))
        # the pool is what the ramp leaves: nothing
        self.assertTrue(all(abs(v) < 1e-9 for v in estimate.pool))

    def test_the_effect_is_per_unit_of_ramp_so_the_25th_carries_all_of_it(self):
        pairs = planted(effect=3.0)
        estimate = self.fit(pairs)
        shift = sc.standardised_shift(estimate, {**{n: 0 for n in cal.ALL_TERMS}, "dom_19_23": 1.0}, None)
        half = sc.standardised_shift(estimate, {**{n: 0 for n in cal.ALL_TERMS}, "dom_19_23": 4 / 7}, None)
        self.assertAlmostEqual(shift, 3.0)
        self.assertAlmostEqual(half, 3.0 * 4 / 7)

    def test_a_ramp_term_enters_the_fit_the_s3_way(self):
        estimate = sc.fit_state_terms(planted(effect=1.0), regressors=(), terms=("dom_19_23",), interact=False, robust=True, training_pairs="direct")
        self.assertIn("dom_19_23", estimate.effect)
        self.assertGreater(estimate.effect["dom_19_23"], 0.0)
        self.assertLess(estimate.effect["dom_19_23"], 1.0)  # ridge 5 and the Huber fit shrink it, as they shrink the flag

    def test_a_one_step_fit_of_the_arms_calendar_columns_is_still_refused_with_no_allow_list_entry(self):
        with self.assertRaisesRegex(ValueError, r"one-step pairs.*served from the scored row"):
            sc.fit_state_terms(planted(1.0), regressors=cal.regressors_of(S3, 1), terms=S3.location, interact=False, robust=True,
                               training_pairs="one_step")
        self.assertFalse([k for k, v in osg.ONE_STEP_ALLOW_LIST.items() if v.fitter == "fit_state_terms"])


class ArmTests(unittest.TestCase):

    def test_the_arm_is_s3_unchanged(self):
        self.assertEqual(S3.name, "sc_s3_robust")
        self.assertEqual(S3.location, cal.NO_FOMC_IORB)
        self.assertIn(gse.REPLACED_TERM, S3.location)
        self.assertTrue(S3.robust and not S3.interact and not S3.sized and S3.extra == () and S3.calendar_k is None)
        self.assertEqual(sc.ridge_of(S3), 5.0)


class WalkTests(unittest.TestCase):

    DAY = date(2024, 6, 20)  # the target of lead 1 is 2024-06-21, a Friday with ramp 3/7

    @classmethod
    def setUpClass(cls):
        cls.walk = sc.walk(PANEL, [cls.DAY], GSE, {}, (S3,), **SETTINGS)
        cls.base = sc.walk(PANEL, [cls.DAY], BASE, {}, (S3,), **SETTINGS)

    def test_the_forecast_exists_with_ordered_quantiles_and_differs_from_s3(self):
        q = self.walk.forecasts["sc_s3_robust"][self.DAY]
        for h in HORIZONS:
            self.assertEqual(len(q[h]), 23)
            self.assertEqual(q[h], sorted(q[h]))
        self.assertNotEqual(q, self.base.forecasts["sc_s3_robust"][self.DAY])

    def test_arm_a_is_unchanged_by_the_ramp(self):
        self.assertEqual(self.walk.forecasts[sc.ARM_A], self.base.forecasts[sc.ARM_A])

    def test_a_forecast_moves_with_its_own_targets_ramp_by_the_effect_times_the_scale(self):
        di = index_of(self.DAY.isoformat())
        target = di + 1
        self.assertEqual(DATES[target], date(2024, 6, 21))
        altered = gse.GseTermTable(PANEL, ANNOUNCEMENTS)
        altered._flags[("dom_19_23", 1)][target] = 0.0  # a row after the decision: no training pair reads it
        other = sc.walk(PANEL, [self.DAY], altered, {}, (S3,), **SETTINGS)
        refit_day = next(iter(self.walk.estimates))
        effect = self.walk.estimates[refit_day]["sc_s3_robust"][1].effect["dom_19_23"]
        scale = self.walk.detail[self.DAY]["scale"]
        a, b = self.walk.forecasts["sc_s3_robust"][self.DAY][1], other.forecasts["sc_s3_robust"][self.DAY][1]
        for x, y in zip(a, b):
            self.assertAlmostEqual(x - y, scale * effect * 3 / 7)
        self.assertNotEqual(effect, 0.0)

    def test_a_future_spread_moves_no_forecast(self):
        import dataclasses

        di = index_of("2024-06-20")
        panel = list(PANEL)
        for i in range(di + 1, len(panel)):
            values = dict(panel[i].values)
            values["sofr"] = float(values["iorb"]) + 40.0
            panel[i] = dataclasses.replace(panel[i], values=values)
        other = sc.walk(panel, [self.DAY], GSE, {}, (S3,), **SETTINGS)
        self.assertEqual(other.forecasts, self.walk.forecasts)

    def test_the_one_step_walk_is_refused(self):
        with self.assertRaisesRegex(ValueError, "one-step pairs"):
            sc.walk(PANEL, [self.DAY], GSE, {}, (S3,), **SETTINGS, training_pairs="one_step")


if __name__ == "__main__":
    unittest.main()
