"""State-scaled calendar effects on scaled mean reversion (#1145; H5 step 3 fix).

`metadata/state_calendar_1145.json` is the declaration; `repo_model.spread_mr_state_calendar` is its arithmetic. What these tests
pin: that an effect is estimated in the model's standardised units, so the effect in bp is the term times the anchor's scale; that
a planted interaction with the scarcity state is recovered and is zero where the state is zero; that the Huber fit lets one
outlier day set less of an effect than least squares does and shrinks a term with few flagged days harder; that the scarcity
state is read as of the decision instant and never later (`LookAheadError`); that the guard of #947 still refuses a one-step fit
and needs no allow-list entry; and that the arm with no state reproduces the standardised arm.

Recorded mutations (each applied to the tree, the named test run, and reverted):

* `read_state`: `if row > decision_index:` replaced with `if row > decision_index + 1:`, so the state of the day after the
  decision (the target-day grid read one row off) is admitted. `test_a_state_after_the_decision_is_refused` failed with
  `AssertionError` (`LookAheadError` not raised).
* `pair_state`: `decision_row = origin + lag` replaced with `decision_row = origin + lag + 1`, so a training pair reads the state
  of the day after its decision. `test_a_training_pair_reads_the_state_of_its_decision_day` failed with `AssertionError`
  (`1.0 != 0.0`).
* `fit_state_terms`: delete the `@guard_one_step_fit` line. `test_a_one_step_fit_of_a_term_column_is_refused_by_the_guard` and
  `test_the_one_step_walk_is_refused` failed with `AssertionError` (the `ValueError` raised was the function's own "direct pairs
  only", not the guard's message naming the column).
"""

from __future__ import annotations

import dataclasses
import unittest
from datetime import date, time
from pathlib import Path

from repo_model import announced_iorb
from repo_model import one_step_guard as osg
from repo_model import spread_mr_calendar as cal
from repo_model import spread_mr_fhs as fhs
from repo_model import spread_mr_state_calendar as sc
from repo_model.splits import LookAheadError

import test_protocol_benchmarks as tpb

ROOT = Path(__file__).resolve().parent.parent
TABLE = ROOT / "tests" / "fixtures" / "snapshots" / "fed-iorb-announcements" / "iorb_changes.csv"
PANEL = tpb.published_panel()["rows"]
ANNOUNCEMENTS = announced_iorb.load_announcements(TABLE)
TABLE_ALL = cal.TermTable(PANEL, ANNOUNCEMENTS)
SETTINGS = dict(registry=tpb.REGISTRY, decision_time=tpb.DECISION, splits=tpb.SPLITS)
NONE = {name: 0 for name in cal.ALL_TERMS}


def index_of(day: str) -> int:
    return next(i for i, row in enumerate(PANEL) if row.date.isoformat() == day)


def states_of(rule) -> dict:
    """A synthetic decision-day state for every panel day."""

    return {row.date: rule(i) for i, row in enumerate(PANEL)}


class SolverTests(unittest.TestCase):

    def test_weights_of_one_are_least_squares(self):
        rows = [[1.0, 0.0], [1.0, 1.0], [1.0, 0.0], [1.0, 1.0]]
        y = [2.0, 5.0, 2.0, 7.0]
        self.assertEqual(sc.solve_weighted(rows, y, [1.0] * 4, 1.0), cal.solve_ridge(rows, y, 1.0))

    def test_a_row_of_weight_zero_is_not_in_the_fit(self):
        rows = [[1.0, 0.0], [1.0, 1.0], [1.0, 1.0], [1.0, 0.0], [1.0, 1.0]]
        y = [2.0, 5.0, 5.0, 2.0, 500.0]
        with_it = sc.solve_weighted(rows, y, [1.0, 1.0, 1.0, 1.0, 0.0], 0.0)
        without = cal.solve_ridge(rows[:4], y[:4], 0.0)
        for a, b in zip(with_it, without):
            self.assertAlmostEqual(a, b)


def planted(effect=3.0, scales=(1.0,), flagged=12, n=80, outlier=None, state=None, slope=0.0):
    """Pairs whose standardised residual is `effect + slope * s` on a quarter-end and noise otherwise."""

    out = []
    for i in range(n):
        flags = dict(NONE)
        flags["quarter_end"] = 1 if i < flagged else 0
        scale = scales[i % len(scales)]
        s = 0.0 if state is None else state(i)
        noise = (-1.0) ** i * (0.4 + (i % 3) * 0.2)
        z = noise + (effect + slope * s if flags["quarter_end"] else 0.0)
        if outlier is not None and i == 0:
            z = outlier
        out.append(sc.StatePair(z * scale, scale, flags, None if state is None else s))
    return out


def fit(pairs, *, interact=False, robust=False, terms=("quarter_end",), regressors=("quarter_end",)):
    return sc.fit_state_terms(pairs, regressors=regressors, terms=terms, interact=interact, robust=robust, training_pairs="direct")


class StandardisedUnitsTests(unittest.TestCase):

    def test_an_effect_proportional_to_the_scale_is_one_number_in_standardised_units(self):
        estimate = fit(planted(effect=3.0, scales=(0.5, 1.0, 4.0)))
        self.assertAlmostEqual(estimate.effect["quarter_end"], 3.0, delta=0.5)

    def test_the_effect_in_bp_is_the_term_times_the_anchors_scale_and_shrinks_in_a_quiet_regime(self):
        estimate = fit(planted(effect=3.0))
        flags = dict(NONE, quarter_end=1)
        loud = sc.lead_quantiles(estimate, centre=10.0, scale=4.0, flags=flags, state=None)
        quiet = sc.lead_quantiles(estimate, centre=10.0, scale=0.5, flags=flags, state=None)
        plain_loud = sc.lead_quantiles(estimate, centre=10.0, scale=4.0, flags=NONE, state=None)
        plain_quiet = sc.lead_quantiles(estimate, centre=10.0, scale=0.5, flags=NONE, state=None)
        for a, b in zip(loud, plain_loud):
            self.assertAlmostEqual(a - b, 4.0 * estimate.effect["quarter_end"])
        for a, b in zip(quiet, plain_quiet):
            self.assertAlmostEqual(a - b, 0.5 * estimate.effect["quarter_end"])
        self.assertEqual(loud, sorted(loud))

    def test_a_term_with_too_few_flagged_pairs_is_absent(self):
        estimate = fit(planted(flagged=sc.MIN_FLAGGED - 1))
        self.assertEqual(estimate.effect, {})
        self.assertEqual(estimate.flagged["quarter_end"], sc.MIN_FLAGGED - 1)

    def test_with_no_term_the_pool_is_the_standardised_residual_pool(self):
        pairs = planted(effect=0.0)
        estimate = fit(pairs, terms=())
        self.assertEqual(estimate.pool, cal.pb.empirical_quantiles(sorted(p.raw / p.scale for p in pairs)))


class InteractionTests(unittest.TestCase):

    STATE = staticmethod(lambda i: (i % 4) / 3.0)

    def test_a_planted_interaction_is_recovered_and_the_effect_is_near_zero_where_the_state_is_zero(self):
        pairs = planted(effect=0.0, slope=6.0, state=self.STATE, flagged=40, n=120)
        estimate = fit(pairs, interact=True)
        self.assertAlmostEqual(estimate.slope["quarter_end"], 6.0, delta=2.0)
        self.assertAlmostEqual(estimate.effect["quarter_end"], 0.0, delta=1.2)
        flags = dict(NONE, quarter_end=1)
        floor = sc.lead_quantiles(estimate, centre=0.0, scale=1.0, flags=flags, state=0.0)
        scarce = sc.lead_quantiles(estimate, centre=0.0, scale=1.0, flags=flags, state=1.0)
        self.assertGreater(scarce[11] - floor[11], 3.5)
        self.assertEqual(scarce, sorted(scarce))

    def test_an_unknown_state_contributes_no_interaction_and_is_counted(self):
        pairs = planted(effect=2.0, slope=0.0, state=self.STATE)
        pairs[5] = pairs[5]._replace(state=None)
        estimate = fit(pairs, interact=True)
        self.assertEqual(estimate.unknown_state, 1)
        flags = dict(NONE, quarter_end=1)
        self.assertEqual(sc.lead_quantiles(estimate, centre=0.0, scale=1.0, flags=flags, state=None),
                         sc.lead_quantiles(estimate, centre=0.0, scale=1.0, flags=flags, state=0.0))

    def test_with_every_state_zero_the_interacted_arm_is_the_plain_one(self):
        pairs = planted(effect=2.0, state=lambda i: 0.0)
        plain, inter = fit(pairs), fit(pairs, interact=True)
        self.assertAlmostEqual(plain.effect["quarter_end"], inter.effect["quarter_end"])
        self.assertEqual(plain.pool, inter.pool)


class RobustTests(unittest.TestCase):

    def test_one_outlier_day_sets_less_of_the_effect_than_least_squares_lets_it(self):
        pairs = planted(effect=2.0, outlier=60.0, flagged=14)
        ols, huber = fit(pairs), fit(pairs, robust=True)
        self.assertLess(huber.effect["quarter_end"], ols.effect["quarter_end"])
        self.assertAlmostEqual(huber.effect["quarter_end"], 2.0, delta=0.8)
        self.assertGreater(ols.effect["quarter_end"], 3.0)

    def test_without_an_outlier_the_robust_effect_is_close_to_the_plain_one(self):
        pairs = planted(effect=2.0, flagged=20)
        self.assertAlmostEqual(fit(pairs).effect["quarter_end"], fit(pairs, robust=True).effect["quarter_end"], delta=0.6)

    def test_a_term_with_few_flagged_days_is_shrunk_harder_than_one_with_many(self):
        few = fit(planted(effect=3.0, flagged=4), robust=True).effect["quarter_end"]
        many = fit(planted(effect=3.0, flagged=30, n=120), robust=True).effect["quarter_end"]
        self.assertLess(few, many)
        self.assertLess(few, 3.0 * 4 / (4 + sc.ROBUST_RIDGE) + 0.6)

    def test_the_robust_fit_stops(self):
        self.assertLessEqual(fit(planted(effect=2.0, outlier=60.0), robust=True).iterations, sc.MAX_ITERATIONS)


class GuardTests(unittest.TestCase):

    def pairs(self):
        return planted(effect=0.0, flagged=5, n=10)

    def test_a_one_step_fit_of_a_term_column_is_refused_by_the_guard(self):
        with self.assertRaisesRegex(ValueError, r"one-step pairs.*served from the scored row"):
            sc.fit_state_terms(self.pairs(), regressors=("quarter_end",), terms=("quarter_end",), interact=False, robust=False,
                               training_pairs="one_step")

    def test_the_direct_fit_is_admitted_with_no_allow_list_entry(self):
        self.assertFalse([k for k, v in osg.ONE_STEP_ALLOW_LIST.items() if v.fitter == "fit_state_terms"])
        self.assertEqual(fit(self.pairs()).pairs, 10)

    def test_a_training_pairing_other_than_direct_is_refused_even_without_a_column(self):
        with self.assertRaisesRegex(ValueError, "direct pairs only"):
            sc.fit_state_terms(self.pairs(), regressors=(), terms=("dom_19_23",), interact=False, robust=False,
                               training_pairs="one_step")


class StateReadTests(unittest.TestCase):

    def test_the_state_of_the_decision_day_is_read(self):
        di = index_of("2024-06-05")
        states = states_of(lambda i: float(i % 4))
        dates = [row.date for row in PANEL]
        self.assertEqual(sc.read_state(states, dates, di, di), states[PANEL[di].date])
        self.assertEqual(sc.read_state(states, dates, di - 3, di), states[PANEL[di - 3].date])

    def test_a_state_after_the_decision_is_refused(self):
        di = index_of("2024-06-05")
        dates = [row.date for row in PANEL]
        states = states_of(lambda i: 1.0)
        with self.assertRaises(LookAheadError):
            sc.read_state(states, dates, di + 1, di)

    def test_a_training_pair_reads_the_state_of_its_decision_day(self):
        di = index_of("2024-06-05")
        dates = [row.date for row in PANEL]
        states = states_of(lambda i: float(i % 4))
        origin, target, lag = di - 8, di - 6, 1
        self.assertEqual(sc.pair_state(states, dates, origin, lag, di), states[dates[origin + lag]])
        self.assertNotEqual(origin + lag, target)
        self.assertNotEqual(sc.pair_state(states, dates, origin, lag, di), states[dates[target]])

    def test_a_missing_or_unknown_state_is_none_and_the_scale_of_the_state_is_a_third_steps(self):
        di = index_of("2024-06-05")
        dates = [row.date for row in PANEL]
        self.assertIsNone(sc.read_state({}, dates, di, di))
        self.assertIsNone(sc.level({PANEL[di].date: None}.get(PANEL[di].date)))
        self.assertEqual([sc.level(v) for v in (0.0, 1.0, 2.0, 3.0)], [0.0, 1 / 3, 2 / 3, 1.0])
        with self.assertRaises(ValueError):
            sc.level(4.0)


class WalkTests(unittest.TestCase):

    DAYS = [row.date for row in PANEL if date(2024, 6, 3) <= row.date <= date(2024, 6, 14)]
    STATES = states_of(lambda i: float((i // 7) % 4))

    @classmethod
    def setUpClass(cls):
        cls.walk = sc.walk(PANEL, cls.DAYS, TABLE_ALL, cls.STATES, **SETTINGS)

    def test_arm_a_is_941s_variant_exactly(self):
        reference = fhs.walk(PANEL, self.DAYS, [fhs.VARIANTS[0]], **SETTINGS)
        self.assertEqual(self.walk.forecasts[sc.ARM_A], reference.forecasts[fhs.VARIANTS[0].name])

    def test_every_arm_has_23_ordered_quantiles_at_every_lead_on_the_same_days(self):
        days = set(self.walk.forecasts[sc.ARM_A])
        self.assertTrue(days)
        for name in sc.ARM_NAMES:
            self.assertEqual(set(self.walk.forecasts[name]), days)
            for leads in self.walk.forecasts[name].values():
                for q in leads.values():
                    self.assertEqual(len(q), 23)
                    self.assertEqual(q, sorted(q))

    def test_the_arms_are_the_declared_four_and_none_reads_a_scale_term(self):
        self.assertEqual([a.name for a in sc.ARMS], ["sc_s1_standardised", "sc_s2_scarcity", "sc_s3_robust", "sc_s4_fomc_iorb"])
        self.assertTrue(all(a.scale == () for a in sc.ARMS))
        self.assertEqual(sc.ARMS[0].location, cal.NO_FOMC_IORB)
        self.assertEqual(sc.ARMS[3].location, cal.ALL_TERMS)
        self.assertEqual([(a.interact, a.robust) for a in sc.ARMS], [(False, False), (True, False), (False, True), (False, False)])

    def test_a_future_spread_moves_no_forecast(self):
        di = index_of("2024-06-07")
        panel = list(PANEL)
        for i in range(di + 1, len(panel)):
            values = dict(panel[i].values)
            values["sofr"] = float(values["iorb"]) + 40.0
            panel[i] = dataclasses.replace(panel[i], values=values)
        other = sc.walk(panel, [PANEL[di].date], TABLE_ALL, self.STATES, **SETTINGS)
        base = sc.walk(PANEL, [PANEL[di].date], TABLE_ALL, self.STATES, **SETTINGS)
        self.assertEqual(other.forecasts, base.forecasts)

    def test_a_future_state_moves_no_forecast(self):
        di = index_of("2024-06-07")
        later = dict(self.STATES)
        for row in PANEL[di + 1:]:
            later[row.date] = 3.0 - (later[row.date] or 0.0)
        base = sc.walk(PANEL, [PANEL[di].date], TABLE_ALL, self.STATES, **SETTINGS)
        other = sc.walk(PANEL, [PANEL[di].date], TABLE_ALL, later, **SETTINGS)
        self.assertEqual(other.forecasts, base.forecasts)

    def test_with_a_constant_zero_state_arm_s2_is_arm_s1(self):
        zero = states_of(lambda i: 0.0)
        walk = sc.walk(PANEL, self.DAYS[:3], TABLE_ALL, zero, **SETTINGS)
        for day, leads in walk.forecasts["sc_s1_standardised"].items():
            for h, q in leads.items():
                for a, b in zip(q, walk.forecasts["sc_s2_scarcity"][day][h]):
                    self.assertAlmostEqual(a, b)

    def test_the_state_changes_arm_s2_and_no_other_arm(self):
        zero = states_of(lambda i: 0.0)
        three = states_of(lambda i: 3.0)
        a = sc.walk(PANEL, self.DAYS[:2], TABLE_ALL, zero, **SETTINGS)
        b = sc.walk(PANEL, self.DAYS[:2], TABLE_ALL, three, **SETTINGS)
        for name in ("sc_s1_standardised", "sc_s3_robust", "sc_s4_fomc_iorb", sc.ARM_A):
            self.assertEqual(a.forecasts[name], b.forecasts[name], name)

    def test_the_one_step_walk_is_refused(self):
        with self.assertRaisesRegex(ValueError, "one-step pairs"):
            sc.walk(PANEL, self.DAYS[:2], TABLE_ALL, self.STATES, **SETTINGS, training_pairs="one_step")

    def test_the_fit_is_renewed_with_the_base_model(self):
        self.assertEqual(len(self.walk.fits), 1)
        self.assertEqual(set(self.walk.estimates), set(self.walk.fits))
        self.assertEqual(set(self.walk.detail), set(self.walk.forecasts[sc.ARM_A]))


if __name__ == "__main__":
    unittest.main()
