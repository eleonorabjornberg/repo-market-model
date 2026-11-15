"""B4, the plain quantile-regression benchmark (#1360; H5, registration design, step 4 to 5; development tier).

`metadata/b4_quantile_regression_1360.json` is the declaration; `repo_model.b4_quantile_regression` is its arithmetic and
`repo_model.protocol_benchmarks.b4_forecast` its entry as a benchmark. What these tests pin: that the solver finds the minimum of the
check loss (against every line through two data points, which contains the exact optimum, and against perturbations); that a planted
effect is recovered and shrunk by the ridge; that a term with too few flagged pairs is absent; that the fitted quantiles are sorted
into a non-crossing set; that a one-step fit of a calendar column is refused by the guard of #947 with no allow-list entry; that the
reserve measure is read as of the decision instant (a Wednesday decision does not see Wednesday's level) and never after the decision
(`LookAheadError`); that a forecast does not change when anything public only after its decision changes; that a calendar effect is
learned at the target day and not one row off (the #914 class); and that the single-decision benchmark of `protocol_benchmarks` is the
walk's fit on the same day.

Recorded mutations (each applied to the tree, the named test run, and reverted):

* `read_reserves`: `if row > decision_index:` replaced with `if row > decision_index + 1:`, so the reserve value of the day after the
  decision is admitted. `ReserveTests.test_a_reserve_read_after_the_decision_is_refused` failed with `AssertionError`
  (`LookAheadError` not raised).
* `ReserveTable.__init__`: `panel[read.row].values.get(RESERVE_COLUMN)` replaced with `panel[row].values.get(RESERVE_COLUMN)`, so a decision reads
  its own row's level, which is public only after the decision. `ReserveTests.test_a_wednesday_decision_does_not_see_the_wednesday_level` failed with
  `AssertionError` (`4.169041 != 4.086336`: the Wednesday level was read on the Wednesday).
* `fit_quantile_regression`: delete the `@guard_one_step_fit` line. `GuardTests.test_a_one_step_fit_of_a_calendar_column_is_refused_by_the_guard`
  failed with `AssertionError` (the `ValueError` raised was the function's own "direct pairs only", not the guard's message naming the
  column).
* `refit`: `flags_at(h, target)` replaced with `flags_at(h, origin)`, so a flag is read from the pair's origin, not from the target (a calendar
  column learned one row off). `TargetDayTests.test_a_quarter_end_target_is_forecast_higher_than_an_ordinary_one` failed with `AssertionError`
  (the quarter-end target's median was 5.85 against 2.04, not above it by 8 bp).
* `training_pairs`: `for target in range(k, anchor + 1)` replaced with `range(k, anchor + 2)`, so a pair's target is the first row not yet
  public. `CausalityTests.test_a_forecast_ignores_what_is_public_only_after_the_decision` and `test_a_pair_never_ends_after_the_anchor` both
  errored with `LookAheadError` (raised by `protocol_benchmarks._require_public`, naming the row after the anchor).
"""

from __future__ import annotations

import random
import unittest
from datetime import date, time

import test_protocol_benchmarks as tpb
from repo_model import b4_quantile_regression as b4
from repo_model.decision_instant import DECISION_TIME
from repo_model import one_step_guard as osg
from repo_model import protocol_benchmarks as pb
from repo_model import scoring_protocol as sp
from repo_model import spread_mr_calendar as cal
from repo_model.data import DailyObservation
from repo_model.splits import LookAheadError

PANEL = tpb.published_panel()["rows"]
DATES = [row.date for row in PANEL]
DECISION = DECISION_TIME  # 18:00 America/New_York, the instant in force (#1312); the panel is built for it
SETTINGS = dict(registry=tpb.REGISTRY, decision_time=DECISION)
NONE = {name: 0 for name in cal.ALL_TERMS}
GRID = sp.GRID


def index_of(day: str, panel=PANEL) -> int:
    return next(i for i, row in enumerate(panel) if row.date.isoformat() == day)


def pair(y, last=0.0, reserves=2.0, **flags):
    return b4.Pair(y, last, reserves, dict(NONE, **flags))


def fit(pairs, *, terms=("quarter_end",), ridge=b4.RIDGE, levels=GRID):
    return b4.fit_quantile_regression(
        osg.stamp_pairs(pairs, direct=True), regressors=("quarter_end", "reserve_balances"), terms=terms, training_pairs="direct", ridge=ridge, levels=levels
    )


def check_loss(pairs, estimate, tau, beta, ridge):
    """The objective of the fit at `beta`: the summed check loss of `tau` plus ridge times the squared non-intercept coefficients."""

    total = 0.0
    for p in pairs:
        row = b4.design_row(p, estimate.terms)
        r = p.response - sum(b * x for b, x in zip(beta, row))
        total += r * (tau - (1.0 if r < 0 else 0.0))
    return total + ridge * sum(b * b for b in beta[1:])


class SolverTests(unittest.TestCase):

    def test_an_intercept_only_fit_is_the_empirical_quantile(self):
        pairs = [pair(float(v), last=0.0, reserves=0.0) for v in range(1, 100)]
        estimate = b4.fit_quantile_regression(
            pairs, regressors=("reserve_balances",), terms=(), training_pairs="direct", ridge=1.0, levels=(0.5, 0.9), min_pairs=1
        )
        self.assertAlmostEqual(estimate.coefficients[0.5][0], 50.0, delta=0.6)
        self.assertAlmostEqual(estimate.coefficients[0.9][0], 90.0, delta=1.1)

    def test_the_fit_reaches_the_optimum_of_the_check_loss_over_every_line_through_two_points(self):
        # With one regressor and no ridge the exact optimum of the check loss interpolates two data points: a line through two of them.
        rng = random.Random(1360)
        xs = [rng.uniform(0.0, 4.0) for _ in range(9)]
        ys = [2.0 + 1.5 * x + rng.gauss(0.0, 1.0) for x in xs]
        pairs = [pair(y, last=x, reserves=0.0) for x, y in zip(xs, ys)]
        for tau in (0.25, 0.5, 0.9):
            estimate = b4.fit_quantile_regression(
                pairs, regressors=("reserve_balances",), terms=(), training_pairs="direct", ridge=1e-6, levels=(tau,), min_pairs=1
            )
            got = check_loss(pairs, estimate, tau, estimate.coefficients[tau], 1e-6)
            best = min(
                check_loss(pairs, estimate, tau, (ys[i] - slope * xs[i], slope, 0.0), 1e-6)
                for i in range(9) for j in range(i + 1, 9) if xs[i] != xs[j]
                for slope in [(ys[j] - ys[i]) / (xs[j] - xs[i])]
            )
            self.assertLessEqual(got, best + 1e-2, f"tau {tau}: the fit's loss {got} is above the best line through two points {best}")

    def test_no_nearby_coefficient_has_a_lower_loss(self):
        rng = random.Random(7)
        pairs = [pair(3.0 + 2.0 * (i % 2) + rng.gauss(0.0, 1.0), last=rng.uniform(-1, 1), reserves=rng.uniform(2, 3), quarter_end=i % 2)
                 for i in range(60)]
        estimate = fit(pairs, levels=(0.1, 0.5, 0.9))
        for tau in (0.1, 0.5, 0.9):
            beta = estimate.coefficients[tau]
            base = check_loss(pairs, estimate, tau, beta, b4.RIDGE)
            for j in range(len(beta)):
                for step in (-0.2, -0.02, 0.02, 0.2):
                    moved = list(beta)
                    moved[j] += step
                    self.assertGreaterEqual(check_loss(pairs, estimate, tau, moved, b4.RIDGE), base - 1e-3)

    def test_a_planted_calendar_effect_is_recovered_at_every_level(self):
        rng = random.Random(3)
        pairs = [pair(5.0 + (6.0 if i % 5 == 0 else 0.0) + rng.uniform(-1.0, 1.0), quarter_end=1 if i % 5 == 0 else 0) for i in range(200)]
        estimate = fit(pairs, ridge=1e-6, levels=(0.25, 0.5, 0.75))
        index = estimate.terms.index("quarter_end") + 3
        for tau in (0.25, 0.5, 0.75):
            self.assertAlmostEqual(estimate.coefficients[tau][index], 6.0, delta=0.5)

    def test_the_ridge_shrinks_a_term_toward_zero(self):
        rng = random.Random(4)
        pairs = [pair(5.0 + (6.0 if i % 5 == 0 else 0.0) + rng.uniform(-1.0, 1.0), quarter_end=1 if i % 5 == 0 else 0) for i in range(60)]
        plain = fit(pairs, ridge=1e-6, levels=(0.5,))
        shrunk = fit(pairs, ridge=50.0, levels=(0.5,))
        index = plain.terms.index("quarter_end") + 3
        self.assertLess(abs(shrunk.coefficients[0.5][index]), abs(plain.coefficients[0.5][index]))

    def test_a_term_with_too_few_flagged_pairs_is_absent(self):
        pairs = [pair(1.0 + i % 3, quarter_end=1 if i < b4.MIN_FLAGGED - 1 else 0) for i in range(80)]
        estimate = fit(pairs, levels=(0.5,))
        self.assertEqual(estimate.terms, ())
        self.assertEqual(estimate.flagged["quarter_end"], b4.MIN_FLAGGED - 1)

    def test_a_pair_with_an_unknown_reserve_value_is_dropped_and_counted(self):
        pairs = [pair(float(i), reserves=None if i < 5 else 2.0) for i in range(80)]
        estimate = fit(pairs, levels=(0.5,))
        self.assertEqual(estimate.pairs, 75)
        self.assertEqual(estimate.unknown_reserves, 5)

    def test_fewer_pairs_than_the_minimum_have_no_fit(self):
        with self.assertRaises(b4.InsufficientHistory):
            fit([pair(float(i)) for i in range(b4.MIN_PAIRS - 1)], levels=(0.5,))

    def test_the_quantiles_are_sorted_into_a_non_crossing_set(self):
        estimate = b4.Estimate(
            terms=(), coefficients={0.1: (5.0, 0.0, 0.0), 0.9: (1.0, 0.0, 0.0), 0.5: (3.0, 0.0, 0.0)}, pairs=100, unknown_reserves=0,
            flagged={}, iterations={0.1: 1, 0.5: 1, 0.9: 1}, levels=(0.1, 0.5, 0.9),
        )
        out = b4.predict(estimate, last=0.0, reserves=2.0, flags=NONE)
        self.assertEqual(out, [1.0, 3.0, 5.0])
        self.assertTrue(b4.crossed(estimate, last=0.0, reserves=2.0, flags=NONE))

    def test_a_fit_on_the_protocols_grid_gives_23_quantiles(self):
        rng = random.Random(5)
        estimate = fit([pair(rng.gauss(2.0, 1.0), last=rng.gauss(2.0, 1.0)) for _ in range(80)], terms=())
        out = b4.predict(estimate, last=2.0, reserves=2.0, flags=NONE)
        self.assertEqual(len(out), len(GRID))
        self.assertEqual(out, sorted(out))


class GuardTests(unittest.TestCase):

    def test_a_one_step_fit_of_a_calendar_column_is_refused_by_the_guard(self):
        """The guard of #947 names the column; the fitter's own refusal of a non-direct fit comes after it."""

        pairs = [pair(float(i), quarter_end=i % 2) for i in range(40)]
        with self.assertRaises(ValueError) as caught:
            b4.fit_quantile_regression(
                pairs, regressors=("quarter_end", "reserve_balances"), terms=("quarter_end",), training_pairs="one_step",
                ridge=1.0, levels=(0.5,),
            )
        self.assertIn("quarter_end", str(caught.exception))
        self.assertIn("served from the scored row itself", str(caught.exception))

    def test_a_direct_fit_needs_no_allow_list_entry(self):
        self.assertFalse([e for e in osg.ONE_STEP_ALLOW_LIST.values() if "quantile_regression" in e.fitter])
        fit([pair(float(i), quarter_end=i % 2) for i in range(80)], levels=(0.5,))

    def test_the_fitter_trains_on_direct_pairs_only(self):
        with self.assertRaises(ValueError):
            b4.fit_quantile_regression(
                [pair(1.0)] * 40, regressors=("reserve_balances",), terms=(), training_pairs="direct_or_not", ridge=1.0, levels=(0.5,)
            )


class ReserveTests(unittest.TestCase):
    table = b4.ReserveTable(PANEL, **SETTINGS)

    def test_a_reserve_read_after_the_decision_is_refused(self):
        with self.assertRaises(LookAheadError):
            self.table.read(500, 499)

    def test_a_reserve_read_at_or_before_the_decision_is_served(self):
        self.assertEqual(self.table.read(499, 499), self.table.read(499, 500))

    def test_a_wednesday_decision_does_not_see_the_wednesday_level(self):
        # 2021-11-10 is a Wednesday. The panel's row carries 4169.041; the level before it, 4086.336, is the one public at the decision.
        day = index_of("2021-11-10")
        self.assertEqual(PANEL[day].values["reserve_balances"], 4169.041)
        self.assertAlmostEqual(self.table.values[day], 4086.336 / b4.RESERVE_UNIT)

    def test_the_value_is_the_latest_public_one_a_day_later(self):
        # 2021-11-15 (a Monday) reads the Wednesday level of 2021-11-10.
        self.assertAlmostEqual(self.table.values[index_of("2021-11-15")], 4169.041 / b4.RESERVE_UNIT)

    def test_the_last_row_has_no_value_because_no_row_follows_it(self):
        self.assertIsNone(self.table.values[-1])


def synthetic(spike=15.0, n_from=0):
    """The published panel's rows with a flat spread of 2 bp plus `spike` on a quarter-end, and reserves held at 2,000."""

    rows = []
    for i, row in enumerate(PANEL):
        values = dict(row.values)
        bump = spike if values.get("quarter_end") else 0.0
        wobble = 0.3 * ((i * 7) % 5 - 2) / 2.0
        values["iorb"] = 4.0
        values["sofr"] = 4.0 + (2.0 + bump + wobble) / 100.0
        values["reserve_balances"] = 2000.0 + (i % 3)
        rows.append(DailyObservation(row.date, values))
    return rows


class TargetDayTests(unittest.TestCase):
    panel = synthetic()
    table = cal.TermTable(panel, ())
    reserves = b4.ReserveTable(panel, **SETTINGS)

    def forecast_on(self, index):
        estimates = b4.refit(self.panel, index, self.table, self.reserves, **SETTINGS, levels=(0.5,))
        return b4.forecast(self.panel, index, estimates, self.table, self.reserves, **SETTINGS)

    def test_a_quarter_end_target_is_forecast_higher_than_an_ordinary_one(self):
        quarter_ends = [i for i, row in enumerate(self.panel) if row.values.get("quarter_end") and i > 600]
        target = quarter_ends[0]
        lead = 3
        ordinary = target - lead - 7  # a decision whose lead-3 target is an ordinary day
        while self.panel[ordinary + lead].values.get("quarter_end") or self.panel[ordinary + lead].values.get("tax_date"):
            ordinary -= 1
        at_turn = self.forecast_on(target - lead)[lead][0]
        at_ordinary = self.forecast_on(ordinary)[lead][0]
        self.assertGreater(at_turn, at_ordinary + 8.0, f"{at_turn} against {at_ordinary}")


class CausalityTests(unittest.TestCase):

    def test_a_forecast_ignores_what_is_public_only_after_the_decision(self):
        index = index_of("2022-06-15")
        anchor = pb._anchor(PANEL, index, registry=tpb.REGISTRY, decision_time=DECISION)
        changed = []
        for i, row in enumerate(PANEL):
            values = dict(row.values)
            if i > anchor:
                values["sofr"] = 9.99
            if i > index:
                values["reserve_balances"] = 1.0
            changed.append(DailyObservation(row.date, values))
        base = self.one(PANEL, index)
        other = self.one(changed, index)
        self.assertEqual(base, other)

    @staticmethod
    def one(panel, index):
        table = cal.TermTable(panel, ())
        reserves = b4.ReserveTable(panel, **SETTINGS)
        estimates = b4.refit(panel, index, table, reserves, **SETTINGS, levels=(0.1, 0.5, 0.9))
        return b4.forecast(panel, index, estimates, table, reserves, **SETTINGS)

    def test_a_pair_never_ends_after_the_anchor(self):
        index = index_of("2022-06-15")
        anchor = pb._anchor(PANEL, index, registry=tpb.REGISTRY, decision_time=DECISION)
        rows = b4.training_pairs(PANEL, index, anchor, lag=index - anchor)
        for h, found in rows.items():
            self.assertTrue(found)
            self.assertLessEqual(max(target for _origin, target in found), anchor)
            for origin, target in found:
                self.assertEqual(target - origin, h + index - anchor)


class WalkTests(unittest.TestCase):
    index = index_of("2022-06-15")
    table = cal.TermTable(PANEL, ())
    reserves = b4.ReserveTable(PANEL, **SETTINGS)

    def test_the_benchmark_of_one_decision_is_the_walks_first_fit(self):
        walked = b4.walk(PANEL, [DATES[self.index], DATES[self.index + 1]], self.table, self.reserves, **SETTINGS, levels=GRID)
        single = pb.b4_forecast(PANEL, self.index, table=self.table, reserves=self.reserves, splits=tpb.SPLITS, **SETTINGS)
        self.assertEqual(walked.forecasts[DATES[self.index]], single)

    def test_the_forecast_has_five_leads_of_23_sorted_quantiles(self):
        out = pb.b4_forecast(PANEL, self.index, table=self.table, reserves=self.reserves, splits=tpb.SPLITS, **SETTINGS)
        self.assertEqual(sorted(out), list(sp.HORIZONS))
        for h, values in out.items():
            self.assertEqual(len(values), len(GRID))
            self.assertEqual(values, sorted(values))

    def test_a_walk_refits_every_21_decision_days_and_between_them_keeps_the_fit(self):
        days = DATES[self.index : self.index + b4.REFIT_EVERY + 2]
        walked = b4.walk(PANEL, days, self.table, self.reserves, **SETTINGS, levels=(0.5,))
        self.assertEqual(sorted(walked.estimates), [days[0], days[b4.REFIT_EVERY]])
        self.assertEqual({walked.fit_used[d] for d in days[: b4.REFIT_EVERY]}, {days[0]})
        self.assertEqual(walked.fit_used[days[b4.REFIT_EVERY]], days[b4.REFIT_EVERY])

    def test_a_scored_decision_day_that_is_not_a_panel_day_is_refused(self):
        with self.assertRaises(sp.ProtocolError):
            b4.walk(PANEL, [date(2022, 6, 18)], self.table, self.reserves, **SETTINGS, levels=(0.5,))

    def test_the_scorer_accepts_the_forecast(self):
        out = pb.b4_forecast(PANEL, self.index, table=self.table, reserves=self.reserves, splits=tpb.SPLITS, **SETTINGS)
        outcomes = {DATES[self.index + h]: PANEL[self.index + h].spread_bps for h in sp.HORIZONS}
        scores = sp.day_scores({DATES[self.index]: out}, outcomes, DATES, score=sp.grid_crps)
        self.assertEqual(list(scores), [DATES[self.index]])


class DeclarationTests(unittest.TestCase):

    def test_the_declaration_names_what_the_module_has(self):
        import json
        from pathlib import Path

        declaration = json.loads((Path(__file__).resolve().parents[1] / "metadata" / "b4_quantile_regression_1360.json").read_text(encoding="utf-8"))
        spec = declaration["b4"]["estimator"]
        self.assertEqual(spec["ridge"], b4.RIDGE)
        self.assertIn(f"EPSILON = {b4.EPSILON:g}", spec["solver"])
        self.assertIn(f"at most {b4.MAX_ITERATIONS} iterations", spec["solver"])
        self.assertTrue(declaration["b4"]["calendar_terms"]["terms"].startswith(
            "month_end, quarter_end, tax_date, settlement_coupon, settlement_bill, dom_19_23 and post_month_end_window"))
        self.assertEqual(b4.TERMS, cal.NO_FOMC_IORB)
        self.assertEqual(declaration["seed"], 1360)
        self.assertEqual(declaration["models"], ["B1", "B1_prime", "B2", "B4", "sc_s3c_ann_net"])


if __name__ == "__main__":
    unittest.main()
