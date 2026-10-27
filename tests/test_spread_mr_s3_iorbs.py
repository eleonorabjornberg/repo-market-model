"""The arm that puts the signed announced IORB change and a technical-adjustment indicator on (s3) (#1227; H5 step 3, avenue #1214).

`metadata/s3_iorbs_1227.json` is the declaration; `repo_model.spread_mr_state_calendar` (`S3_IORBS`, `IorbTable`) is its arithmetic. The
arm is (s3) (Huber fit, ridge 5, the seven terms of (s3), no state) with `iorb_window` and two terms beside it: `iorb_signed`, the signed
`iorb_announced_change_bps` over the rows of the window the lead can read, in units of 25 bp, and `iorb_technical`, 1 where a change in
that window is not a multiple of 25 bp (`setup_diagnostic.is_technical`). Both are scheduled fields of the target row, so they are read
at the target day on direct pairs and only where `asof` rule 2 admits them, exactly as the flag `iorb_window` is: the day of the change
and the two panel days after it, at the leads the flag reads (1 to 3), and absent at leads 4 and 5.

What these tests pin: that the arm is (s3) plus those three terms and nothing else; that the earlier arms are unchanged; that the
signed value and the indicator are read from the target row and the two rows after the change, never from an announcement the decision
could not have seen (the availability test, below); that a term with fewer than three non-zero pairs does not enter; that the Huber fit
lets an outlier day set less of the effect; that the one-step fit is refused by the guard of #947; and that the arm, walked alone or
with (s3), gives the forecasts it gives in company.

Recorded mutation (applied to the tree, the named test run, and reverted):

* `IorbTable.at`: `offsets = cal.readable_offsets(cal.TERM["iorb_window"], lead)` replaced with `offsets = cal.TERM["iorb_window"].span`,
  so the table reads the day of a change and the two rows after it at every lead, including the day of the change at a lead-2 decision
  (a row whose value is public only on the panel day before it, after that decision). `test_the_signed_change_is_not_read_before_it_is_public`
  failed with `AssertionError` (`{'iorb_signed': -1.2, 'iorb_technical': 1.0} != {'iorb_signed': 0.0, 'iorb_technical': 0.0}`);
  `test_a_note_announced_after_the_decision_moves_no_read_at_it` and `test_the_terms_are_absent_at_leads_4_and_5` failed with
  `AssertionError` too.
"""

from __future__ import annotations

import dataclasses
import unittest
from datetime import date, time

from repo_model import announced_iorb
from repo_model import setup_diagnostic
from repo_model import spread_mr_calendar as cal
from repo_model import spread_mr_state_calendar as sc

from test_spread_mr_state_calendar import ANNOUNCEMENTS, NONE, PANEL, SETTINGS, TABLE_ALL, index_of, states_of

S3 = sc.ARMS[2]
ARM = sc.S3_IORBS
EXTRAS = ("iorb_signed", "iorb_technical")
TABLE = sc.IorbTable(PANEL, ANNOUNCEMENTS)
#: The panel day a -30 bp change (2019-09-19, announced 2019-09-18 14:00; not a multiple of 25) takes effect.
TECHNICAL_DAY = "2019-09-19"
#: A -25 bp change (2019-08-01), not technical.
ORDINARY_DAY = "2019-08-01"


def fit(pairs, *, terms=("quarter_end", "iorb_window"), extra=EXTRAS, robust=True):
    return sc.fit_state_terms(
        pairs, regressors=("iorb_announced_change_bps",), terms=terms, interact=False, robust=robust, ridge=5.0, extra=extra,
        training_pairs="direct",
    )


def planted(signed_effect=-2.0, technical_effect=0.0, n=120, windows=16, technical_days=6, outlier=None):
    """Pairs whose standardised residual is `signed_effect` per 25 bp of change (and `technical_effect` on a technical change) plus noise.

    The first `windows` pairs sit in an IORB window with alternating changes of +25 and -25 bp (a +20 bp one among them, technical);
    the first `technical_days` of them carry the technical change.
    """

    out = []
    for i in range(n):
        flags = dict(NONE)
        extras = {"iorb_signed": 0.0, "iorb_technical": 0.0}
        if i < windows:
            flags["iorb_window"] = 1
            technical = i < technical_days
            change = (20.0 if i % 2 == 0 else -30.0) if technical else (25.0 if i % 2 == 0 else -25.0)
            extras = {"iorb_signed": change / sc.IORB_UNIT_BPS, "iorb_technical": 1.0 if technical else 0.0}
        noise = (-1.0) ** i * (0.4 + (i % 3) * 0.2)
        z = noise + signed_effect * extras["iorb_signed"] + technical_effect * extras["iorb_technical"]
        if outlier is not None and i == 0:
            z = outlier
        out.append(sc.StatePair(z, 1.0, flags, None, {}, -1, -1, extras))
    return out


class DeclaredArmTests(unittest.TestCase):

    def test_the_arm_is_s3_with_the_iorb_window_and_the_two_terms_and_nothing_else(self):
        self.assertEqual(ARM.name, "sc_s3_iorbs")
        self.assertEqual(dataclasses.replace(ARM, name=S3.name, role=S3.role, location=S3.location, extra=()), S3)
        self.assertEqual((ARM.robust, ARM.interact, ARM.sized, sc.ridge_of(ARM)), (True, False, False, 5.0))
        self.assertEqual(ARM.extra, EXTRAS)

    def test_the_location_terms_are_those_of_s3_and_iorb_window_and_not_the_fomc_day(self):
        self.assertEqual(ARM.location, tuple(n for n in cal.ALL_TERMS if n in cal.NO_FOMC_IORB or n == "iorb_window"))
        self.assertIn("iorb_window", ARM.location)
        self.assertNotIn("fomc_day", ARM.location)
        self.assertEqual(set(ARM.location) - set(S3.location), {"iorb_window"})

    def test_the_arm_is_registered_and_the_earlier_arms_are_unchanged(self):
        self.assertIs(sc.ALL_ARMS[ARM.name], ARM)
        self.assertEqual([a.name for a in sc.S3_IORBS_ARMS], [S3.name, ARM.name])
        self.assertEqual([a.name for a in sc.S3_TERMS], [S3.name, "sc_s3_state", "sc_s3_fomc_iorb"])
        self.assertEqual([a.name for a in sc.DECOMPOSITION], ["sc_s1_standardised", "sc_r1_ridge5", "sc_r2_huber", "sc_s3_robust", "sc_r3_size"])
        self.assertEqual([(sc.ridge_of(a), a.robust, a.interact, a.sized, a.extra) for a in sc.ARMS],
                         [(1.0, False, False, False, ()), (1.0, False, True, False, ()), (5.0, True, False, False, ()),
                          (1.0, False, False, False, ())])

    def test_a_technical_change_is_the_rule_of_the_setup_diagnostic(self):
        self.assertIs(sc.technical, setup_diagnostic.is_technical)
        self.assertEqual([sc.technical(x) for x in (25, -25, 50, 75, -100, 0)], [False] * 6)
        self.assertEqual([sc.technical(x) for x in (20, -5, -30, 5)], [True] * 4)


class IorbTableTests(unittest.TestCase):
    """The availability of the signed change and the indicator at the target day."""

    def at(self, day, lead, offset=0):
        return TABLE.at(lead, index_of(day) + offset)

    def test_the_day_of_the_change_and_the_two_rows_after_it_carry_the_signed_change_at_lead_1(self):
        for offset in (0, 1, 2):
            got = self.at(TECHNICAL_DAY, 1, offset)
            self.assertAlmostEqual(got["iorb_signed"], -30.0 / 25.0)
            self.assertEqual(got["iorb_technical"], 1.0)
        after = self.at(TECHNICAL_DAY, 1, 3)
        self.assertEqual((after["iorb_signed"], after["iorb_technical"]), (0.0, 0.0))

    def test_a_multiple_of_25_bp_is_signed_and_not_technical(self):
        got = self.at(ORDINARY_DAY, 1)
        self.assertAlmostEqual(got["iorb_signed"], -1.0)
        self.assertEqual(got["iorb_technical"], 0.0)

    def test_a_day_with_no_change_is_zero_and_the_sign_is_the_sign_of_the_change(self):
        self.assertEqual(self.at("2024-06-05", 1), {"iorb_signed": 0.0, "iorb_technical": 0.0})
        self.assertGreater(self.at("2022-03-17", 1)["iorb_signed"], 0.0)  # +25 bp: a hike
        self.assertLess(self.at("2024-09-19", 1)["iorb_signed"], 0.0)  # -50 bp: a cut

    def test_the_signed_change_is_not_read_before_it_is_public(self):
        """The row of a change is public on the panel day before it: a lead-2 decision cannot read the day of the change (offset 0)
        and reads it only from the next row, a lead-3 decision only from the second row after (the same offsets as the flag)."""

        self.assertEqual(self.at(TECHNICAL_DAY, 2, 0), {"iorb_signed": 0.0, "iorb_technical": 0.0})
        self.assertAlmostEqual(self.at(TECHNICAL_DAY, 2, 1)["iorb_signed"], -30.0 / 25.0)
        self.assertAlmostEqual(self.at(TECHNICAL_DAY, 2, 2)["iorb_signed"], -30.0 / 25.0)
        self.assertEqual(self.at(TECHNICAL_DAY, 3, 0), {"iorb_signed": 0.0, "iorb_technical": 0.0})
        self.assertEqual(self.at(TECHNICAL_DAY, 3, 1), {"iorb_signed": 0.0, "iorb_technical": 0.0})
        self.assertAlmostEqual(self.at(TECHNICAL_DAY, 3, 2)["iorb_signed"], -30.0 / 25.0)

    def test_the_terms_are_absent_at_leads_4_and_5(self):
        for lead in (4, 5):
            self.assertEqual(self.at(TECHNICAL_DAY, lead, 2), {})
            self.assertFalse(cal.available(cal.TERM["iorb_window"], lead))

    def test_the_forecast_reads_the_same_as_the_training_row_at_every_readable_lead(self):
        for lead in (1, 2, 3):
            row = index_of(TECHNICAL_DAY) + 2
            self.assertEqual(TABLE.read(lead, row - lead), TABLE.at(lead, row))

    def test_a_note_announced_after_the_decision_moves_no_read_at_it(self):
        """The 2019-09-19 note, made larger: no read at a decision before its announcement (2019-09-18 14:00, public at the 16:00
        decision of the 18th, the panel day before the 19th) moves, at any lead; the read at the 18th for the 19th does."""

        changed = tuple(
            a._replace(change_bps=-55, rate_bps=a.rate_bps - 25) if a.effective == date(2019, 9, 19) else a for a in ANNOUNCEMENTS
        )
        other = sc.IorbTable(PANEL, changed)
        target = index_of(TECHNICAL_DAY)
        for lead in (1, 2, 3):
            for decision in range(target - lead - 4, target - 1):
                self.assertEqual(TABLE.read(lead, decision), other.read(lead, decision), (lead, decision))
        self.assertNotEqual(TABLE.read(1, target - 1), other.read(1, target - 1))
        self.assertAlmostEqual(other.read(1, target - 1)["iorb_signed"], -55.0 / 25.0)

    def test_the_cut_announced_on_the_sunday_is_never_in_the_column(self):
        """2020-03-16 (-100 bp, announced Sunday 17:00): the column is built on the announcement time, so neither the day nor the two
        after it carry it (the existing flag does not either)."""

        for offset in (0, 1, 2):
            self.assertEqual(self.at("2020-03-16", 1, offset), {"iorb_signed": 0.0, "iorb_technical": 0.0})

    def test_the_signed_change_of_the_table_is_the_column_of_announced_iorb(self):
        column = announced_iorb.announced_iorb_features([r.date for r in PANEL], ANNOUNCEMENTS, decision_time=time(16, 0))
        for row in (index_of("2019-05-02"), index_of("2022-06-16"), index_of("2024-09-19"), index_of("2024-06-05")):
            self.assertAlmostEqual(TABLE.at(1, row)["iorb_signed"], (column[row]["iorb_announced_change_bps"] or 0.0) / 25.0)


class FitTests(unittest.TestCase):

    def test_a_planted_signed_effect_is_recovered_with_the_ridge_shrinking_it(self):
        estimate = fit(planted(signed_effect=-2.0))
        self.assertGreater(estimate.iterations, 0)  # a Huber fit
        self.assertLess(estimate.effect["iorb_signed"], -1.0)
        self.assertGreater(estimate.effect["iorb_signed"], -2.6)

    def test_the_signed_term_moves_the_forecast_by_its_effect_times_the_scale_in_the_direction_of_the_change(self):
        estimate = fit(planted(signed_effect=-2.0))
        flags = dict(NONE, iorb_window=1)
        cut = sc.lead_quantiles(estimate, centre=0.0, scale=3.0, flags=flags, state=None, extras={"iorb_signed": -2.0, "iorb_technical": 0.0})
        hike = sc.lead_quantiles(estimate, centre=0.0, scale=3.0, flags=flags, state=None, extras={"iorb_signed": 2.0, "iorb_technical": 0.0})
        none = sc.lead_quantiles(estimate, centre=0.0, scale=3.0, flags=flags, state=None, extras={"iorb_signed": 0.0, "iorb_technical": 0.0})
        beta = estimate.effect["iorb_signed"]
        for a, b, c in zip(cut, none, hike):
            self.assertAlmostEqual(a - b, 3.0 * beta * -2.0)
            self.assertAlmostEqual(c - b, 3.0 * beta * 2.0)

    def test_the_technical_indicator_is_estimated_beside_the_signed_change(self):
        estimate = fit(planted(signed_effect=0.0, technical_effect=3.0, technical_days=8))
        self.assertGreater(estimate.effect["iorb_technical"], 1.0)
        self.assertIn("iorb_window", estimate.effect)

    def test_a_term_with_fewer_than_three_nonzero_pairs_does_not_enter_and_is_counted(self):
        estimate = fit(planted(technical_effect=3.0, technical_days=sc.MIN_FLAGGED - 1))
        self.assertNotIn("iorb_technical", estimate.effect)
        self.assertEqual(estimate.flagged["iorb_technical"], sc.MIN_FLAGGED - 1)
        self.assertIn("iorb_signed", estimate.effect)
        none = fit(planted(windows=sc.MIN_FLAGGED - 1, technical_days=0))
        self.assertNotIn("iorb_signed", none.effect)
        self.assertNotIn("iorb_window", none.effect)

    def test_the_arm_without_the_extras_ignores_them_and_is_s3_with_iorb_window(self):
        pairs = planted()
        plain = fit(pairs, extra=())
        self.assertNotIn("iorb_signed", plain.effect)
        self.assertNotIn("iorb_technical", plain.effect)
        reference = sc.fit_state_terms(pairs, regressors=("iorb_announced_change_bps",), terms=("quarter_end", "iorb_window"),
                                       interact=False, robust=True, ridge=5.0, training_pairs="direct")
        self.assertEqual(plain.effect, reference.effect)
        self.assertEqual(plain.pool, reference.pool)

    def test_pairs_without_the_extras_fit_the_flag_alone(self):
        """At leads 4 and 5 no extra is readable: the pairs carry none and the fit is the flag's."""

        bare = [p._replace(extras={}) for p in planted()]
        estimate = fit(bare)
        self.assertNotIn("iorb_signed", estimate.effect)
        self.assertNotIn("iorb_signed", estimate.flagged)

    def test_the_pool_is_the_residual_after_the_extras_too(self):
        pairs = planted(signed_effect=-2.0)
        with_extra, without = fit(pairs), fit(pairs, extra=())
        window = [i for i, p in enumerate(pairs) if p.flags["iorb_window"]]
        spread_with = max(abs(with_extra.residuals[i]) for i in window)
        spread_without = max(abs(without.residuals[i]) for i in window)
        self.assertLess(spread_with, spread_without)

    def test_an_outlier_change_day_sets_less_of_the_effect_under_the_huber_fit_than_under_least_squares(self):
        pairs = planted(signed_effect=-2.0, outlier=60.0)
        huber = fit(pairs)
        ols = fit(pairs, robust=False)
        self.assertLess(abs(huber.effect["iorb_signed"] - -2.0), abs(ols.effect["iorb_signed"] - -2.0))

    def test_the_state_interaction_is_refused_with_the_extras(self):
        with self.assertRaisesRegex(ValueError, "interact"):
            sc.fit_state_terms(planted(), regressors=("iorb_announced_change_bps",), terms=("iorb_window",), interact=True, robust=True,
                               ridge=5.0, extra=EXTRAS, training_pairs="direct")

    def test_a_one_step_fit_of_the_iorb_column_is_refused_by_the_guard(self):
        with self.assertRaisesRegex(ValueError, r"one-step pairs.*served from the scored row"):
            sc.fit_state_terms(planted(), regressors=("iorb_announced_change_bps",), terms=("iorb_window",), interact=False, robust=True,
                               ridge=5.0, extra=EXTRAS, training_pairs="one_step")


class WalkTests(unittest.TestCase):

    DAYS = [row.date for row in PANEL if date(2024, 6, 3) <= row.date <= date(2024, 6, 14)]
    STATES = states_of(lambda i: 0.0)

    @classmethod
    def setUpClass(cls):
        cls.walk = sc.walk(PANEL, cls.DAYS, TABLE_ALL, cls.STATES, sc.S3_IORBS_ARMS, **SETTINGS, iorb=TABLE)

    def test_the_arm_has_23_ordered_quantiles_at_every_lead_on_the_days_of_the_comparators(self):
        days = set(self.walk.forecasts[sc.ARM_A])
        self.assertTrue(days)
        for arm in sc.S3_IORBS_ARMS:
            self.assertEqual(set(self.walk.forecasts[arm.name]), days)
            for leads in self.walk.forecasts[arm.name].values():
                for q in leads.values():
                    self.assertEqual(len(q), 23)
                    self.assertEqual(q, sorted(q))

    def test_s3_in_company_is_the_s3_of_1145(self):
        reference = sc.walk(PANEL, self.DAYS, TABLE_ALL, self.STATES, **SETTINGS)
        self.assertEqual(self.walk.forecasts[S3.name], reference.forecasts[S3.name])

    def test_the_arm_alone_gives_the_forecasts_it_gives_in_company(self):
        alone = sc.walk(PANEL, self.DAYS, TABLE_ALL, self.STATES, (ARM,), **SETTINGS, iorb=TABLE)
        self.assertEqual(alone.forecasts[ARM.name], self.walk.forecasts[ARM.name])

    def test_the_extras_are_estimated_at_leads_1_to_3_and_absent_at_leads_4_and_5(self):
        for estimates in self.walk.estimates.values():
            for h in (1, 2, 3):
                est = estimates[ARM.name][h]
                self.assertTrue(set(EXTRAS) <= set(est.flagged), h)
                self.assertIn("iorb_window", est.flagged)
            for h in (4, 5):
                est = estimates[ARM.name][h]
                self.assertFalse(set(EXTRAS) & set(est.flagged), h)
                self.assertFalse({"iorb_window", *EXTRAS} & set(est.effect), h)
            self.assertFalse(set(EXTRAS) & set(estimates[S3.name][1].effect))

    def test_a_walk_of_the_arm_needs_the_table(self):
        with self.assertRaisesRegex(ValueError, "IORB table"):
            sc.walk(PANEL, self.DAYS[:2], TABLE_ALL, self.STATES, (ARM,), **SETTINGS)

    def test_a_change_after_the_decision_moves_no_forecast(self):
        di = index_of("2024-06-07")
        far = tuple(a._replace(change_bps=-50, rate_bps=a.rate_bps - 25) if a.effective == date(2024, 9, 19) else a for a in ANNOUNCEMENTS)
        base = sc.walk(PANEL, [PANEL[di].date], TABLE_ALL, self.STATES, sc.S3_IORBS_ARMS, **SETTINGS, iorb=TABLE)
        other = sc.walk(PANEL, [PANEL[di].date], TABLE_ALL, self.STATES, sc.S3_IORBS_ARMS, **SETTINGS, iorb=sc.IorbTable(PANEL, far))
        self.assertEqual(base.forecasts, other.forecasts)

    def test_the_one_step_walk_is_refused_by_the_guard(self):
        with self.assertRaisesRegex(ValueError, "one-step pairs"):
            sc.walk(PANEL, self.DAYS[:2], TABLE_ALL, self.STATES, (ARM,), **SETTINGS, iorb=TABLE, training_pairs="one_step")


if __name__ == "__main__":
    unittest.main()
