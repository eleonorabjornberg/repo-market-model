"""The two arms that put terms on (s3)'s robust fit (#1196; H5 step 3): (s3+state) and (s3+FOMC/IORB).

`metadata/s3_terms_1196.json` is the declaration; `repo_model.spread_mr_state_calendar` (`S3_STATE`, `S3_CAL`, `S3_TERMS`) is its
arithmetic and adds no estimator: both arms are flags on `fit_state_terms`. What these tests pin: that (s3+state) is (s3) with the
interaction (same Huber fit, same ridge of 5, same terms) and (s3+FOMC/IORB) is (s3) with `fomc_day` and `iorb_window` (the terms of
(s4), the same Huber fit and ridge of 5); that the arms of #1145 and #1172 are unchanged; that the Huber fit damps an outlier day
under the interaction and under the FOMC term, which is the point of the avenue; that with every state zero (s3+state) is (s3); that
the FOMC and IORB terms are read at the target day on direct pairs and enter only (s3+FOMC/IORB); that a state after the decision
moves no forecast of either arm; and that the one-step fit of either arm is refused by the guard of #947.

No new guard is added (the state reader, the term reader and the one-step guard are the ones of #1145, with their recorded
mutations in `test_spread_mr_state_calendar`), so there is no mutation to record here.
"""

from __future__ import annotations

import dataclasses
import unittest
from datetime import date

from repo_model import spread_mr_calendar as cal
from repo_model import spread_mr_state_calendar as sc

from test_spread_mr_state_calendar import NONE, PANEL, SETTINGS, TABLE_ALL, index_of, planted, states_of

S3 = sc.ARMS[2]
S4 = sc.ARMS[3]


def fit(pairs, arm, *, terms=("quarter_end",)):
    return sc.fit_state_terms(
        pairs, regressors=terms, terms=terms, interact=arm.interact, robust=arm.robust, ridge=arm.ridge, sized=arm.sized,
        training_pairs="direct",
    )


def with_fomc(n=90, effect=2.0, outlier=None, flagged=12):
    """Pairs whose standardised residual is `effect` on an FOMC day and noise otherwise; pair 0 may be an outlier FOMC day."""

    out = []
    for i in range(n):
        flags = dict(NONE)
        flags["fomc_day"] = 1 if i < flagged else 0
        noise = (-1.0) ** i * (0.4 + (i % 3) * 0.2)
        z = noise + (effect if flags["fomc_day"] else 0.0)
        if outlier is not None and i == 0:
            z = outlier
        out.append(sc.StatePair(z, 1.0, flags, None))
    return out


class DeclaredArmsTests(unittest.TestCase):

    def test_state_arm_is_s3_with_the_interaction_and_nothing_else(self):
        self.assertEqual(sc.S3_STATE.name, "sc_s3_state")
        self.assertEqual(
            dataclasses.replace(sc.S3_STATE, name=S3.name, role=S3.role, interact=False), S3)
        self.assertTrue(sc.S3_STATE.interact)
        self.assertTrue(sc.S3_STATE.robust)
        self.assertEqual(sc.ridge_of(sc.S3_STATE), 5.0)
        self.assertEqual(sc.S3_STATE.location, cal.NO_FOMC_IORB)
        self.assertFalse(sc.S3_STATE.sized)

    def test_fomc_iorb_arm_is_s3_with_the_terms_of_s4_and_nothing_else(self):
        self.assertEqual(sc.S3_CAL.name, "sc_s3_fomc_iorb")
        self.assertEqual(
            dataclasses.replace(sc.S3_CAL, name=S3.name, role=S3.role, location=S3.location), S3)
        self.assertEqual(sc.S3_CAL.location, S4.location)
        self.assertEqual(sc.S3_CAL.location, cal.ALL_TERMS)
        self.assertEqual((sc.S3_CAL.robust, sc.S3_CAL.interact, sc.ridge_of(sc.S3_CAL)), (True, False, 5.0))

    def test_the_screen_is_s3_then_the_two_arms_and_is_registered(self):
        self.assertEqual([a.name for a in sc.S3_TERMS], [S3.name, sc.S3_STATE.name, sc.S3_CAL.name])
        for arm in sc.S3_TERMS:
            self.assertIs(sc.ALL_ARMS[arm.name], arm)

    def test_the_arms_of_1145_and_1172_are_unchanged(self):
        self.assertEqual([(sc.ridge_of(a), a.robust, a.interact, a.sized) for a in sc.ARMS],
                         [(1.0, False, False, False), (1.0, False, True, False), (5.0, True, False, False), (1.0, False, False, False)])
        self.assertEqual([a.name for a in sc.DECOMPOSITION], ["sc_s1_standardised", "sc_r1_ridge5", "sc_r2_huber", "sc_s3_robust", "sc_r3_size"])
        self.assertEqual(len(sc.ALL_ARMS), 9)


class RobustInteractionTests(unittest.TestCase):

    STATE = staticmethod(lambda i: (i % 4) / 3.0)

    def test_a_planted_interaction_is_recovered_under_the_huber_fit_with_the_ridge_of_5(self):
        pairs = planted(effect=0.0, slope=6.0, state=self.STATE, flagged=40, n=120)
        estimate = fit(pairs, sc.S3_STATE)
        self.assertGreater(estimate.iterations, 0)  # a Huber fit, not least squares
        self.assertGreater(estimate.slope["quarter_end"], 2.5)  # the ridge of 5 shrinks it, so not the planted 6 itself
        self.assertLess(estimate.slope["quarter_end"], 6.5)
        flags = dict(NONE, quarter_end=1)
        floor = sc.lead_quantiles(estimate, centre=0.0, scale=1.0, flags=flags, state=0.0)
        scarce = sc.lead_quantiles(estimate, centre=0.0, scale=1.0, flags=flags, state=1.0)
        self.assertGreater(scarce[11] - floor[11], 2.0)

    def test_an_outlier_day_sets_less_of_the_slope_under_the_huber_fit_than_under_least_squares(self):
        pairs = planted(effect=0.0, slope=2.0, state=self.STATE, flagged=40, n=120)
        pairs[0] = pairs[0]._replace(raw=80.0)  # a flagged day with state 0 and a huge residual (March 2020)
        least_squares = fit(pairs, dataclasses.replace(sc.S3_STATE, robust=False))
        robust = fit(pairs, sc.S3_STATE)
        self.assertLess(abs(robust.effect["quarter_end"]), abs(least_squares.effect["quarter_end"]))

    def test_with_every_state_zero_the_arm_is_s3(self):
        pairs = planted(effect=2.0, state=lambda i: 0.0, flagged=20)
        plain, inter = fit(pairs, S3), fit(pairs, sc.S3_STATE)
        self.assertAlmostEqual(plain.effect["quarter_end"], inter.effect["quarter_end"], places=6)
        self.assertEqual(plain.pool, inter.pool)


class RobustFomcTests(unittest.TestCase):

    TERMS = ("fomc_day",)

    def test_the_fomc_term_enters_only_when_it_is_a_location_term_of_the_arm(self):
        pairs = with_fomc()
        with_term = fit(pairs, sc.S3_CAL, terms=self.TERMS)
        self.assertIn("fomc_day", with_term.effect)
        # (s3) has no FOMC location term: `terms` are the arm's, so the fit of (s3) on the same pairs carries none
        without = sc.fit_state_terms(pairs, regressors=(), terms=S3.location, interact=False, robust=True, training_pairs="direct")
        self.assertNotIn("fomc_day", without.effect)

    def test_the_huber_fit_lets_an_outlier_rate_change_day_set_less_of_the_fomc_effect(self):
        pairs = with_fomc(effect=2.0, outlier=60.0, flagged=14)
        ols = fit(pairs, dataclasses.replace(sc.S3_CAL, robust=False, ridge=5.0), terms=self.TERMS)
        huber = fit(pairs, sc.S3_CAL, terms=self.TERMS)
        self.assertLess(huber.effect["fomc_day"], ols.effect["fomc_day"])
        self.assertAlmostEqual(huber.effect["fomc_day"], 2.0, delta=1.0)


class WalkTests(unittest.TestCase):

    DAYS = [row.date for row in PANEL if date(2024, 6, 3) <= row.date <= date(2024, 6, 14)]
    STATES = states_of(lambda i: float((i // 7) % 4))

    @classmethod
    def setUpClass(cls):
        cls.walk = sc.walk(PANEL, cls.DAYS, TABLE_ALL, cls.STATES, sc.S3_TERMS, **SETTINGS)

    def test_every_arm_has_23_ordered_quantiles_at_every_lead_on_the_same_days(self):
        days = set(self.walk.forecasts[sc.ARM_A])
        self.assertTrue(days)
        for arm in sc.S3_TERMS:
            self.assertEqual(set(self.walk.forecasts[arm.name]), days)
            for leads in self.walk.forecasts[arm.name].values():
                for q in leads.values():
                    self.assertEqual(len(q), 23)
                    self.assertEqual(q, sorted(q))

    def test_the_arms_alone_give_the_forecasts_they_give_in_company(self):
        alone = sc.walk(PANEL, self.DAYS, TABLE_ALL, self.STATES, (sc.S3_STATE,), **SETTINGS)
        self.assertEqual(alone.forecasts[sc.S3_STATE.name], self.walk.forecasts[sc.S3_STATE.name])
        self.assertEqual(alone.forecasts[sc.ARM_A], self.walk.forecasts[sc.ARM_A])

    def test_s3_in_the_screen_is_the_s3_of_1145(self):
        reference = sc.walk(PANEL, self.DAYS, TABLE_ALL, self.STATES, **SETTINGS)
        self.assertEqual(self.walk.forecasts[S3.name], reference.forecasts[S3.name])

    def test_the_state_changes_the_state_arm_and_no_other(self):
        zero, three = states_of(lambda i: 0.0), states_of(lambda i: 3.0)
        a = sc.walk(PANEL, self.DAYS[:2], TABLE_ALL, zero, sc.S3_TERMS, **SETTINGS)
        b = sc.walk(PANEL, self.DAYS[:2], TABLE_ALL, three, sc.S3_TERMS, **SETTINGS)
        for name in (S3.name, sc.S3_CAL.name, sc.ARM_A):
            self.assertEqual(a.forecasts[name], b.forecasts[name], name)

    def test_a_future_state_moves_no_forecast_of_either_arm(self):
        di = index_of("2024-06-07")
        later = dict(self.STATES)
        for row in PANEL[di + 1:]:
            later[row.date] = 3.0 - (later[row.date] or 0.0)
        base = sc.walk(PANEL, [PANEL[di].date], TABLE_ALL, self.STATES, sc.S3_TERMS, **SETTINGS)
        other = sc.walk(PANEL, [PANEL[di].date], TABLE_ALL, later, sc.S3_TERMS, **SETTINGS)
        self.assertEqual(other.forecasts, base.forecasts)

    def test_the_one_step_walk_of_either_arm_is_refused_by_the_guard(self):
        for arm in (sc.S3_STATE, sc.S3_CAL):
            with self.assertRaisesRegex(ValueError, "one-step pairs"):
                sc.walk(PANEL, self.DAYS[:2], TABLE_ALL, self.STATES, (arm,), **SETTINGS, training_pairs="one_step")

    def test_the_fomc_and_iorb_terms_are_in_the_estimate_of_the_calendar_arm_only(self):
        for estimates in self.walk.estimates.values():
            for h, est in estimates[S3.name].items():
                self.assertFalse({"fomc_day", "iorb_window"} & set(est.terms), h)
            for h, est in estimates[sc.S3_STATE.name].items():
                self.assertFalse({"fomc_day", "iorb_window"} & set(est.terms), h)
            self.assertTrue(set(estimates[sc.S3_CAL.name][1].flagged) >= {"fomc_day", "iorb_window"})
            self.assertIn("iorb_window", estimates[sc.S3_CAL.name][1].flagged)

    def test_the_state_arm_has_a_slope_for_each_entering_term_and_the_others_have_none(self):
        for estimates in self.walk.estimates.values():
            for h in (1, 3):
                self.assertEqual(set(estimates[sc.S3_STATE.name][h].slope), set(estimates[sc.S3_STATE.name][h].effect))
                self.assertEqual(estimates[S3.name][h].slope, {})
                self.assertEqual(estimates[sc.S3_CAL.name][h].slope, {})


if __name__ == "__main__":
    unittest.main()
