"""(s3c-carry): (s3c) with a month-end carryover term sized to the spike (#1275; H5 step 3).

`metadata/s3c_carry_1275.json` is the declaration; `repo_model.s3c_carry` is its arithmetic. What these tests pin: the business day of the
month and the month-end row it names; the declared decay (1 on business day 1, 0.5 on business day 2, 0 elsewhere) and the floor of the
spike at 0; the availability rule (the month-end spread is read only if it was public at the decision instant, else the term is 0, never
an earlier month's spike) and the `LookAheadError` for a row after the anchor; that a month-end spread nobody could yet read moves no
forecast and one that was public does; that the fit recovers a planted carryover fraction, shrunk by the ridge, divides the column by the
scale, and leaves every other term as (s3)'s fit has it; that where the term is not active the estimate and the forecast are (s3)'s, element
for element; that the effect in bp is the coefficient times the column; and that the one-step guard still refuses a one-step fit.

Recorded mutations (each applied to the tree, confirmed by grep, the named test run, and reverted):

* `carry_value`: `if end is None or end > anchor:` replaced with `if end is None or end > anchor + 1:`, so a month-end spread of the day of
  the decision (public the next morning) is admitted. Four tests failed with `LookAheadError` (raised by the guard of `spike_bp`, which
  `carry_value` then reached with a row after the anchor): `test_a_month_end_not_yet_public_gives_zero_not_a_leak`, the two `RefitTests`
  (training pairs whose month-end is after their origin) and the `WalkTests` class set-up (the walk's own decision days).
* `spike_bp`: the `pb._require_public([row], anchor, ...)` line deleted. `test_a_spike_after_the_anchor_is_refused` failed with
  `AssertionError` (`LookAheadError` not raised); the other 27 tests passed, which is why `carry_value` carries its own rule too.
* `refit`: `carry.append(carry_value(panel, levels, target, origin))` replaced with `carry.append(carry_value(panel, levels, target, anchor))`,
  so a training pair reads the month-end as of the decision's anchor instead of its own origin. Three tests failed with `AssertionError`:
  `test_a_training_pair_reads_the_month_end_as_of_its_origin` (a lead beyond the first became active), `test_every_lead_beyond_the_first_is_s3s_estimate_exactly`
  and `test_a_lead_where_the_column_is_zero_and_not_active_is_s3s_forecast` (lists differ).
* `fit_carry_terms`: the `@guard_one_step_fit` line deleted. `test_a_one_step_fit_is_refused_by_the_guard` failed with `AssertionError`
  (`'tax_date'` not found in the function's own "trains on direct pairs only" message, so the guard's refusal naming the column was gone).
"""

from __future__ import annotations

import dataclasses
import unittest
from datetime import date, timedelta
from pathlib import Path

from repo_model import protocol_benchmarks as pb
from repo_model import s3c_carry as cc
from repo_model import spread_mean_reversion as smr
from repo_model import spread_mr_calendar as cal
from repo_model import spread_mr_state_calendar as sc
from repo_model.data import DailyObservation
from repo_model.splits import LookAheadError

import test_protocol_benchmarks as tpb

ROOT = Path(__file__).resolve().parent.parent
PANEL = tpb.published_panel()["rows"]
SETTINGS = dict(registry=tpb.REGISTRY, decision_time=tpb.DECISION, splits=tpb.SPLITS)
REFIT = dict(registry=tpb.REGISTRY, decision_time=tpb.DECISION)
LEVELS = smr.ordinary_levels(PANEL, tpb.SPLITS)
NONE = {name: 0 for name in cal.ALL_TERMS}


def index_of(day: str, panel=PANEL) -> int:
    return next(i for i, row in enumerate(panel) if row.date.isoformat() == day)


def with_sofr(panel, day: str, sofr_percent: float):
    """`panel` with SOFR of `day` replaced (the spread of that row changes, nothing else)."""

    out = list(panel)
    i = index_of(day, panel)
    out[i] = DailyObservation(panel[i].date, {**panel[i].values, "sofr": sofr_percent})
    return out


def days(*iso):
    return [date.fromisoformat(x) for x in iso]


class CalendarTests(unittest.TestCase):

    DATES = days("2024-04-29", "2024-04-30", "2024-05-01", "2024-05-02", "2024-05-03", "2024-05-06")

    def test_the_business_day_is_the_market_day_of_the_month(self):
        self.assertEqual([cc.business_day(d) for d in self.DATES[2:]], [1, 2, 3, 4])
        self.assertEqual(cc.business_day(date(2024, 7, 5)), 4)  # 4 July is a holiday

    def test_the_month_end_is_the_last_row_of_the_month_before(self):
        self.assertEqual([cc.month_end_row(self.DATES, i) for i in range(2, 6)], [1, 1, 1, 1])
        self.assertIsNone(cc.month_end_row(self.DATES, 0))
        self.assertIsNone(cc.month_end_row(self.DATES, 1))

    def test_a_panel_that_starts_inside_a_month_has_no_month_end_for_it(self):
        self.assertIsNone(cc.month_end_row([r.date for r in PANEL], 0))

    def test_the_decay_is_the_declared_one(self):
        self.assertEqual(dict(cc.DECAY), {1: 1.0, 2: 0.5})


class ValueTests(unittest.TestCase):
    """May 2024: the 31st (Friday) is the month-end, 3 June business day 1, 4 June business day 2, 5 June business day 3."""

    E = index_of("2024-05-31")

    def spike(self):
        return max(0.0, PANEL[self.E].spread_bps - LEVELS[self.E])

    def test_business_day_1_carries_the_whole_spike_and_business_day_2_half(self):
        spiked = with_sofr(PANEL, "2024-05-31", 7.0)
        levels = smr.ordinary_levels(spiked, tpb.SPLITS)
        spike = spiked[self.E].spread_bps - levels[self.E]
        self.assertGreater(spike, 0.0)
        anchor = self.E + 5
        self.assertAlmostEqual(cc.carry_value(spiked, levels, self.E + 1, anchor), spike)
        self.assertAlmostEqual(cc.carry_value(spiked, levels, self.E + 2, anchor), 0.5 * spike)
        self.assertEqual(cc.carry_value(spiked, levels, self.E + 3, anchor), 0.0)
        self.assertEqual(cc.carry_value(spiked, levels, self.E - 5, anchor), 0.0)

    def test_the_spike_is_floored_at_zero(self):
        low = with_sofr(PANEL, "2024-05-31", 0.5)
        levels = smr.ordinary_levels(low, tpb.SPLITS)
        self.assertLess(low[self.E].spread_bps, levels[self.E])
        self.assertEqual(cc.spike_bp(low, levels, self.E, self.E), 0.0)
        self.assertEqual(cc.carry_value(low, levels, self.E + 1, self.E + 3), 0.0)

    def test_a_spike_after_the_anchor_is_refused(self):
        with self.assertRaises(LookAheadError):
            cc.spike_bp(PANEL, LEVELS, self.E, self.E - 1)
        self.assertGreaterEqual(cc.spike_bp(PANEL, LEVELS, self.E, self.E), 0.0)

    def test_a_month_end_not_yet_public_gives_zero_not_a_leak(self):
        spiked = with_sofr(PANEL, "2024-05-31", 9.0)
        levels = smr.ordinary_levels(spiked, tpb.SPLITS)
        # the anchor is the day before the month-end: the spread of the 31st is not public, the term is 0 on business days 1 and 2
        self.assertEqual(cc.carry_value(spiked, levels, self.E + 1, self.E - 1), 0.0)
        self.assertEqual(cc.carry_value(spiked, levels, self.E + 2, self.E - 1), 0.0)
        # and no earlier month-end is read in its place
        self.assertEqual(cc.carry_value(spiked, levels, self.E + 1, self.E - 1), cc.carry_value(PANEL, LEVELS, self.E + 1, self.E - 1))
        # public as of its own day: read
        self.assertGreater(cc.carry_value(spiked, levels, self.E + 2, self.E), 0.0)

    def test_the_spike_is_zero_where_the_level_is_undefined(self):
        self.assertIsNone(LEVELS[0])
        self.assertEqual(cc.spike_bp(PANEL, LEVELS, 0, 0), 0.0)


def planted(effect=0.6, n=80, flagged=20, spike=4.0, carry_scale=1.0, noise=0.3):
    """Pairs whose standardised residual is `effect * carry / scale` where the carry column is positive, and noise (deterministic) elsewhere."""

    pairs, carry = [], []
    for i in range(n):
        x = spike * (1.0 if i % 2 else 0.5) if i < flagged else 0.0
        scale = carry_scale
        jitter = noise * (((i * 37) % 11) - 5) / 5.0
        pairs.append(sc.StatePair(scale * (effect * x / scale + jitter), scale, dict(NONE), None, {}, i, i + 1, {}, False))
        carry.append(x)
    return pairs, carry


FIT = dict(regressors=(), terms=cal.NO_FOMC_IORB, training_pairs="direct")


class FitTests(unittest.TestCase):

    def test_a_planted_carryover_fraction_is_recovered_and_shrunk_by_the_ridge(self):
        pairs, carry = planted()
        est = cc.fit_carry_terms(pairs, carry, **FIT)
        self.assertTrue(est.active)
        self.assertEqual(est.carry_pairs, 20)
        self.assertGreater(est.coefficient, 0.3)
        self.assertLess(est.coefficient, 0.6)  # ridge 5 shrinks toward 0

    def test_the_fit_equals_the_direct_huber_solution_on_the_same_design(self):
        pairs, carry = planted(noise=0.3)
        est = cc.fit_carry_terms(pairs, carry, **FIT)
        design = [[1.0, x / p.scale] for p, x in zip(pairs, carry)]
        beta, _ = sc.huber(design, [p.raw / p.scale for p in pairs], sc.ROBUST_RIDGE)
        self.assertAlmostEqual(est.coefficient, beta[1], places=12)

    def test_the_column_is_divided_by_the_scale_of_the_pair(self):
        pairs, carry = planted(carry_scale=2.0, noise=0.3)
        est = cc.fit_carry_terms(pairs, carry, **FIT)
        design = [[1.0, x / p.scale] for p, x in zip(pairs, carry)]
        beta, _ = sc.huber(design, [p.raw / p.scale for p in pairs], sc.ROBUST_RIDGE)
        self.assertAlmostEqual(est.coefficient, beta[1], places=12)
        undivided, _ = sc.huber([[1.0, x] for x in carry], [p.raw / p.scale for p in pairs], sc.ROBUST_RIDGE)
        self.assertNotAlmostEqual(est.coefficient, undivided[1], places=3)

    def test_the_pool_is_what_the_term_leaves(self):
        pairs, carry = planted()
        est = cc.fit_carry_terms(pairs, carry, **FIT)
        residuals = sorted(p.raw / p.scale - est.coefficient * x / p.scale for p, x in zip(pairs, carry))
        self.assertEqual(list(est.state.pool), list(pb.empirical_quantiles(residuals)))

    def test_fewer_than_three_positive_columns_leave_the_estimate_as_s3s(self):
        pairs, carry = planted(flagged=2)
        est = cc.fit_carry_terms(pairs, carry, **FIT)
        plain = sc.fit_state_terms(pairs, regressors=(), terms=cal.NO_FOMC_IORB, interact=False, robust=True, training_pairs="direct")
        self.assertFalse(est.active)
        self.assertEqual(est.coefficient, 0.0)
        self.assertEqual(est.state, plain)
        self.assertEqual(est.carry_pairs, 2)

    def test_the_flag_terms_are_s3s_when_the_carry_column_is_all_zero(self):
        pairs = []
        for i in range(60):
            flags = dict(NONE)
            flags["quarter_end"] = 1 if i < 12 else 0
            pairs.append(sc.StatePair(3.0 * flags["quarter_end"] + 0.1 * (i % 5), 1.0, flags, None, {}, i, i + 1, {}, False))
        est = cc.fit_carry_terms(pairs, [0.0] * 60, **FIT)
        plain = sc.fit_state_terms(pairs, regressors=(), terms=cal.NO_FOMC_IORB, interact=False, robust=True, training_pairs="direct")
        self.assertEqual(est.state, plain)

    def test_with_the_carry_active_the_other_terms_still_enter_and_are_fitted_jointly(self):
        pairs, carry = [], []
        for i in range(80):
            flags = dict(NONE)
            flags["quarter_end"] = 1 if 40 <= i < 55 else 0
            x = 4.0 if i < 20 else 0.0
            pairs.append(sc.StatePair(2.0 * flags["quarter_end"] + 0.5 * x + 0.3 * (((i * 37) % 11) - 5) / 5.0, 1.0, flags, None, {}, i, i + 1, {}, False))
            carry.append(x)
        est = cc.fit_carry_terms(pairs, carry, **FIT)
        self.assertIn("quarter_end", est.state.effect)
        self.assertGreater(est.state.effect["quarter_end"], 1.0)
        self.assertGreater(est.coefficient, 0.1)
        self.assertEqual(est.state.flagged[cc.CARRY], 20)

    def test_the_effect_in_bp_is_the_coefficient_times_the_column(self):
        pairs, carry = planted()
        est = cc.fit_carry_terms(pairs, carry, **FIT)
        q = [float(i) for i in range(23)]
        out = cc.forecast_leads({1: est, 2: dataclasses.replace(est, coefficient=0.0)}, {1: q, 2: q}, {1: 3.0, 2: 3.0})
        self.assertEqual(out[1], [v + est.coefficient * 3.0 for v in q])
        self.assertEqual(out[2], q)

    def test_a_one_step_fit_is_refused_by_the_guard(self):
        pairs, carry = planted()
        with self.assertRaises(ValueError) as caught:
            cc.fit_carry_terms(pairs, carry, regressors=("tax_date",), terms=cal.NO_FOMC_IORB, training_pairs="one_step")
        self.assertIn("tax_date", str(caught.exception))

    def test_one_carry_value_per_pair(self):
        pairs, carry = planted()
        with self.assertRaises(ValueError):
            cc.fit_carry_terms(pairs, carry[:-1], **FIT)


class RefitTests(unittest.TestCase):

    D = index_of("2024-06-03")  # decision day: its anchor is 31 May, the month-end

    def setUp(self):
        table = cal.TermTable(PANEL, [])
        base = smr.fit(PANEL, self.D, levels=LEVELS, **SETTINGS)
        self.table, self.base = table, base

    def test_a_training_pair_reads_the_month_end_as_of_its_origin(self):
        mine, s3 = cc.refit(PANEL, self.D, self.table, levels=LEVELS, base=self.base, **REFIT)
        lag = self.D - pb._anchor(PANEL, self.D, tpb.REGISTRY, tpb.DECISION)
        anchor = self.D - lag
        rows = smr.training_rows(PANEL, self.D, anchor, lag=lag, levels=LEVELS)
        # lead 1: a pair whose target is business day 2 and whose origin is the day before the month-end has a zero column
        for origin, target in rows[1]:
            end = cc.month_end_row([r.date for r in PANEL], target)
            col = cc.carry_value(PANEL, LEVELS, target, origin)
            if end is not None and end > origin:
                self.assertEqual(col, 0.0)
        pairs_before = [(o, t) for o, t in rows[1]
                        if cc.DECAY.get(cc.business_day(PANEL[t].date), 0.0) and cc.month_end_row([r.date for r in PANEL], t) > o]
        self.assertTrue(pairs_before)
        for h in (2, 3, 4, 5):
            self.assertFalse(mine[h].active, f"lead {h}: the month-end is never public for a business-day target")
            self.assertEqual(mine[h].carry_pairs, 0)
        self.assertGreater(mine[1].carry_pairs, 0)
        self.assertEqual(sorted(s3), sorted(mine))

    def test_every_lead_beyond_the_first_is_s3s_estimate_exactly(self):
        mine, s3 = cc.refit(PANEL, self.D, self.table, levels=LEVELS, base=self.base, **REFIT)
        for h in (2, 3, 4, 5):
            self.assertEqual(mine[h].state, s3[h])


class WalkTests(unittest.TestCase):
    """The walk around the end of May 2024: 30 May, 31 May (the month-end), 3 June (business day 1), 4 June."""

    DAYS = days("2024-05-30", "2024-05-31", "2024-06-03", "2024-06-04", "2024-06-05")

    @classmethod
    def setUpClass(cls):
        cls.table = cal.TermTable(PANEL, [])
        cls.walk = cc.walk(PANEL, cls.DAYS, cls.table, **SETTINGS)

    def test_s3_here_is_the_state_calendar_walks_s3_forecast_for_forecast(self):
        theirs = sc.walk(PANEL, self.DAYS, self.table, {}, (sc.ARMS[2],), **SETTINGS)
        self.assertEqual(self.walk.s3, theirs.forecasts[sc.ARMS[2].name])

    def test_the_column_is_read_only_where_the_month_end_was_public(self):
        v = self.walk.values
        # decision on the month-end (anchor the 30th): the spread of the 31st is not public; business day 1 and 2 targets read 0
        self.assertEqual(v[date(2024, 5, 31)], {h: 0.0 for h in range(1, 6)})
        # decision on business day 1 (anchor the 31st): lead 1 is business day 2 and reads half the spike
        end = index_of("2024-05-31")
        spike = max(0.0, PANEL[end].spread_bps - LEVELS[end])
        self.assertAlmostEqual(v[date(2024, 6, 3)][1], 0.5 * spike)
        for h in (2, 3, 4, 5):
            self.assertEqual(v[date(2024, 6, 3)][h], 0.0)
        # decision on 30 May: business day 1 is lead 2; not public
        self.assertEqual(v[date(2024, 5, 30)], {h: 0.0 for h in range(1, 6)})

    def test_a_lead_where_the_column_is_zero_and_not_active_is_s3s_forecast(self):
        for d in self.DAYS:
            for h in (2, 3, 4, 5):
                self.assertEqual(self.walk.forecasts[d][h], self.walk.s3[d][h], (d, h))

    def test_every_forecast_has_23_ordered_quantiles(self):
        for leads in self.walk.forecasts.values():
            for q in leads.values():
                self.assertEqual(len(q), 23)
                self.assertEqual(q, sorted(q))

    def test_a_forecast_does_not_read_the_spread_of_the_decision_day(self):
        """The spread of the month-end moves no forecast made on the month-end, and a forecast made the next day reads it."""

        spiked = with_sofr(PANEL, "2024-05-31", 12.0)
        table = cal.TermTable(spiked, [])
        on_end = cc.walk(spiked, days("2024-05-31"), table, **SETTINGS)
        base = cc.walk(PANEL, days("2024-05-31"), self.table, **SETTINGS)
        self.assertEqual(on_end.forecasts, base.forecasts)
        self.assertEqual(on_end.values, base.values)
        after = cc.walk(spiked, days("2024-06-03"), table, **SETTINGS)
        plain = cc.walk(PANEL, days("2024-06-03"), self.table, **SETTINGS)
        self.assertNotEqual(after.values[date(2024, 6, 3)][1], plain.values[date(2024, 6, 3)][1])
        self.assertGreater(after.values[date(2024, 6, 3)][1], 0.0)

    def test_a_future_spread_moves_no_forecast(self):
        later = with_sofr(PANEL, "2024-06-07", 15.0)
        other = cc.walk(later, self.DAYS, cal.TermTable(later, []), **SETTINGS)
        self.assertEqual(other.forecasts, self.walk.forecasts)

    def test_the_decision_day_of_the_walk_is_refused_off_the_panel(self):
        from repo_model.scoring_protocol import ProtocolError

        with self.assertRaises(ProtocolError):
            cc.walk(PANEL, [date(2024, 6, 1)], self.table, **SETTINGS)


if __name__ == "__main__":
    unittest.main()
