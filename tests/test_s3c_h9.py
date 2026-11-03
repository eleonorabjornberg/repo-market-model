"""A richer target's forecast as a continuous input of (s3c-ann-net) (#1345; H9 step 3, development tier).

`repo_model.s3c_h9.TargetForecastTable` serves a target walk's lead-h median to `spread_mr_state_calendar` as the extra term `h9_forecast`, and the
fit centres it. Pinned on hand cases: the value a training pair and a forecast read is the one made on the decision row `lead` rows before the target row
(the direct pair of a label day, finding #915); a unit divides it; a decision day without a forecast serves nothing; the fit centres the term on the pairs
that have it, gives a pair without it the value of its mean, enters it only when at least `H9_MIN_OBSERVED` pairs have it, and with no forecast on any
pair is the base arm's fit to the bit; a served value is centred on the fit's mean and a missing one shifts nothing.

**Recorded mutation** (1 November 2026), in `TargetForecastTable._value` (a forecast must come from a fit made at or before its own decision day): the line

    if fit > day:

was changed to `if False:`. `AvailabilityTests.test_a_forecast_from_a_later_fit_is_refused` then failed with `AssertionError: LookAheadError not raised`;
restored, it passes. Second mutation, in the same method (a forecast with no recorded fit has no known instant): the line

    if fit is None:

was changed to `if False:`. `AvailabilityTests.test_a_forecast_with_no_recorded_fit_is_refused` then failed with `TypeError: '>' not supported between
instances of 'datetime.date' and 'NoneType'` (the guard gone, the comparison reached it). Third mutation, in `spread_mr_state_calendar.extra_value` (a
missing centred term is its mean, so it adds nothing): `return extras[name] - centre[name] if name in extras else 0.0` was changed to
`return extras[name] - centre[name] if name in extras else 1.0`; `FitTests.test_a_pair_without_the_forecast_adds_nothing` then failed with
`AssertionError` (the pool moved).
"""

from __future__ import annotations

import sys
import unittest
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from repo_model import s3c_h9, spread_mr_state_calendar as sc  # noqa: E402
from repo_model.splits import LookAheadError  # noqa: E402


def business_days(first, n):
    day, out = first, []
    while len(out) < n:
        if day.weekday() < 5:
            out.append(day)
        day += timedelta(days=1)
    return out


DAYS = business_days(date(2026, 3, 2), 12)


def table(medians, fits=None, *, unit=1.0, lead=2):
    fits = {d: d for d in medians} if fits is None else fits
    return s3c_h9.TargetForecastTable(DAYS, {lead: medians}, {lead: fits}, unit=unit)


class AlignmentTests(unittest.TestCase):
    def test_a_target_row_reads_the_forecast_made_lead_rows_before(self):
        t = table({DAYS[3]: 7.0, DAYS[4]: 9.0})
        self.assertEqual(t.at(2, 5), {sc.H9_FORECAST: 7.0})
        self.assertEqual(t.at(2, 6), {sc.H9_FORECAST: 9.0})

    def test_a_forecast_reads_its_own_decision_days_value(self):
        t = table({DAYS[3]: 7.0, DAYS[4]: 9.0})
        self.assertEqual(t.read(2, 3), {sc.H9_FORECAST: 7.0})
        self.assertEqual(t.read(2, 4), t.at(2, 6))

    def test_a_day_without_a_forecast_serves_nothing_not_another_days(self):
        t = table({DAYS[3]: 7.0, DAYS[4]: None})
        self.assertEqual(t.read(2, 4), {})
        self.assertEqual(t.read(2, 5), {})
        self.assertEqual(t.at(2, 1), {})  # the decision row would be before the panel
        self.assertEqual(t.at(3, 6), {})  # a lead the table has no walk for

    def test_the_unit_divides_the_median(self):
        self.assertEqual(table({DAYS[3]: 250.0}, unit=100.0).read(2, 3), {sc.H9_FORECAST: 2.5})
        with self.assertRaises(ValueError):
            table({}, unit=0.0)

    def test_units_are_declared_for_every_target(self):
        from repo_model import target_forecasts as tf

        self.assertEqual(set(s3c_h9.UNITS), set(tf.TARGETS))


class AvailabilityTests(unittest.TestCase):
    def test_a_forecast_from_a_later_fit_is_refused(self):
        t = table({DAYS[3]: 7.0}, {DAYS[3]: DAYS[4]})
        with self.assertRaises(LookAheadError):
            t.read(2, 3)
        with self.assertRaises(LookAheadError):
            t.at(2, 5)

    def test_a_forecast_from_the_same_days_fit_is_read(self):
        self.assertEqual(table({DAYS[3]: 7.0}, {DAYS[3]: DAYS[3]}).read(2, 3), {sc.H9_FORECAST: 7.0})

    def test_a_forecast_with_no_recorded_fit_is_refused(self):
        with self.assertRaises(LookAheadError):
            table({DAYS[3]: 7.0}, {}).read(2, 3)


def pair(x, raw, i):
    extras = {} if x is None else {sc.H9_FORECAST: x}
    return sc.StatePair(raw, 1.0, {}, None, {}, i, i + 1, extras)


def fit(pairs, extra=(sc.H9_FORECAST,)):
    return sc.fit_state_terms(pairs, regressors=(), terms=(), interact=False, robust=True, training_pairs="direct", extra=extra)


class FitTests(unittest.TestCase):
    def pairs(self, n=80, slope=0.5):
        xs = [float(i % 7) for i in range(n)]
        mean = sum(xs) / n
        return [pair(x, slope * (x - mean) + 0.01 * ((-1) ** i), i) for i, x in enumerate(xs)], mean

    def test_the_term_is_centred_on_the_pairs_that_have_it(self):
        pairs, mean = self.pairs()
        estimate = fit(pairs)
        self.assertIn(sc.H9_FORECAST, estimate.effect)
        self.assertAlmostEqual(estimate.centre[sc.H9_FORECAST], mean, places=9)
        self.assertGreater(estimate.effect[sc.H9_FORECAST], 0.3)

    def test_a_served_value_is_centred_on_the_fits_mean(self):
        pairs, mean = self.pairs()
        estimate = fit(pairs)
        shift = sc.standardised_shift(estimate, {}, None, None, {sc.H9_FORECAST: mean + 2.0})
        self.assertAlmostEqual(shift, 2.0 * estimate.effect[sc.H9_FORECAST], places=9)
        self.assertAlmostEqual(sc.standardised_shift(estimate, {}, None, None, {sc.H9_FORECAST: mean}), 0.0, places=9)

    def test_a_missing_served_value_shifts_nothing(self):
        estimate = fit(self.pairs()[0])
        self.assertEqual(sc.standardised_shift(estimate, {}, None, None, {}), 0.0)

    def test_a_pair_without_the_forecast_adds_nothing(self):
        pairs, _ = self.pairs()
        with_hole = pairs + [pair(None, 0.0, 99)]
        a, b = fit(pairs), fit(with_hole)
        self.assertEqual(b.pairs, a.pairs + 1)
        self.assertEqual(len(b.residuals), len(a.residuals) + 1)
        self.assertAlmostEqual(b.centre[sc.H9_FORECAST], a.centre[sc.H9_FORECAST], places=12)
        # the pair without the forecast sits at the mean: its residual is its raw value (0), whatever the effect
        self.assertEqual(b.residuals[-1], 0.0)

    def test_too_few_pairs_with_the_forecast_keep_it_out_of_the_fit(self):
        pairs, _ = self.pairs(n=sc.H9_MIN_OBSERVED - 1)
        estimate = fit(pairs)
        self.assertNotIn(sc.H9_FORECAST, estimate.effect)
        self.assertEqual(estimate.centre, {})
        self.assertEqual(estimate.flagged[sc.H9_FORECAST], sc.H9_MIN_OBSERVED - 1)

    def test_with_no_forecast_on_any_pair_the_fit_is_the_base_fit(self):
        bare = [pair(None, 0.2 * ((-1) ** i) + 0.05 * (i % 3), i) for i in range(80)]
        plus, base = fit(bare), fit(bare, extra=())
        self.assertEqual(plus.effect, base.effect)
        self.assertEqual(list(plus.pool), list(base.pool))
        self.assertEqual(plus.centre, {})

    def test_other_extras_are_unchanged(self):
        pairs = [sc.StatePair(0.5 * (i % 3), 1.0, {}, None, {}, i, i + 1, {sc.IORB_SIGNED: float(i % 3)}) for i in range(30)]
        estimate = fit(pairs, extra=(sc.IORB_SIGNED,))
        self.assertIn(sc.IORB_SIGNED, estimate.effect)
        self.assertEqual(estimate.centre, {})
        self.assertAlmostEqual(sc.standardised_shift(estimate, {}, None, None, {sc.IORB_SIGNED: 2.0}), 2.0 * estimate.effect[sc.IORB_SIGNED])


if __name__ == "__main__":
    unittest.main()
