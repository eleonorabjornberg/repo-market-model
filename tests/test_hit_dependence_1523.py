"""The helpers of `scripts/hit_dependence_1523.py` (#1523; H5, step M5 registration, development tier).

The study diagnoses the serial dependence of the candidate (s3c-ann-net)'s quantile hits under the amendment 4 coverage design: where it
sits (lead, level, regime, day type), what drives it (the information lag, a level or a scale that adapts too slowly) and what three
post-hoc adjustments of the quantile output would do to grid CRPS and to the coverage cells. It adds no scoring rule, fits no model and
changes no threshold. What these tests pin:

- the hit rule is the design's strict one, and the ordinal code the study feeds `coverage_size_1516.cell_p_values` reproduces exactly the
  strict hits at the four read levels;
- the thinned rows at spacing s are the design's rows (every s-th decision day by order within a regime);
- the lift arithmetic on hand cases (independence is 1, a hit that always follows a hit is above it);
- the online adjustments never read an outcome that is not public at the decision day (the guard below), and each reduces to the
  unadjusted forecast when it has nothing to learn from;
- a forecaster that is calibrated by construction and reads data to the panel day D - 1 for a target D + h shows lag-1 dependence of its
  hits that the design's spacing s = h reads as dependence and spacing s = h + 1 does not (the structural part of the finding);
- the constants are the declaration's (`metadata/hit_dependence_1523.json`); the study reads the development window only.

Recorded mutations for the look-ahead guard (a new availability guard), both run and restored:
- in `public_count`, `bisect.bisect_right(target_positions, decision_pos - 1)` changed to `bisect.bisect_right(target_positions, decision_pos)`:
  `GuardTests.test_the_resolved_cells_of_a_lead_stop_at_the_day_before_the_decision` fails with `AssertionError: Lists differ: [0, 1, 2] != [0, 1]`,
  and `test_an_outcome_not_yet_public_never_moves_the_adjusted_forecast` fails with `repo_model.splits.LookAheadError` (the raising guard catches the
  leak that the count lets through);
- in `require_public`, `if target_pos >= decision_pos:` changed to `if target_pos > decision_pos:`:
  `GuardTests.test_a_target_that_is_not_public_is_refused` fails with `AssertionError: LookAheadError not raised`.
"""

from __future__ import annotations

import importlib.util
import json
import random
import sys
import unittest
from datetime import date, timedelta
from pathlib import Path
from statistics import NormalDist

from repo_model import scoring_protocol as sp
from repo_model.splits import LookAheadError

ROOT = Path(__file__).resolve().parent.parent
_spec = importlib.util.spec_from_file_location("hit_dependence_1523", ROOT / "scripts" / "hit_dependence_1523.py")
script = importlib.util.module_from_spec(_spec)
sys.modules["hit_dependence_1523"] = script
_spec.loader.exec_module(script)

N = NormalDist()
MED = sp.GRID.index(0.5)
DECLARATION = json.loads((ROOT / "metadata" / "hit_dependence_1523.json").read_text(encoding="utf-8"))


def business_days(start: date, n: int):
    out, d = [], start
    while len(out) < n:
        if d.weekday() < 5:
            out.append(d)
        d += timedelta(days=1)
    return out


def walk_doc(n_days: int = 120, seed: int = 3, phi: float = 0.6, scale: float = 1.0, shift: float = 0.0):
    """A development walk file: an AR(1) spread, and per cell the quantiles of a forecaster that reads to the panel day D - 1 and knows phi."""

    rng = random.Random(seed)
    calendar = business_days(date(2019, 3, 4), n_days + 8)
    y, prev = {}, 0.0
    for d in calendar:
        prev = phi * prev + rng.gauss(0, 1)
        y[d] = prev
    days = calendar[2:2 + n_days]
    pos = {d: i for i, d in enumerate(calendar)}
    cells, models, targets, outcome = [], [], {}, {}
    for d in days:
        for h in sp.HORIZONS:
            t = calendar[pos[d] + h]
            mean = (phi ** (h + 1)) * y[calendar[pos[d] - 1]] + shift
            sd = scale * (sum(phi ** (2 * i) for i in range(h + 1))) ** 0.5
            cells.append([d.isoformat(), h, t.isoformat()])
            models.append([mean + sd * N.inv_cdf(level) for level in sp.GRID])
            outcome[t.isoformat()] = y[t]
            targets[t.isoformat()] = {"regime": "r", "types": ["ordinary"], "pressure": "ordinary"}
    return {
        "window": "development", "calendar": [d.isoformat() for d in calendar], "cells": cells, "outcome": outcome, "targets": targets,
        "regime_of_day": {d.isoformat(): ("a" if i < n_days // 2 else "b") for i, d in enumerate(days)},
        "models": {script.CANDIDATE: models}, "panel_sha256": "x",
    }


class HitRuleTests(unittest.TestCase):
    def quantiles(self):
        return [N.inv_cdf(level) for level in sp.GRID]

    def test_the_hit_is_strict_and_beyond_the_level(self):
        q = self.quantiles()
        i95, i05 = sp.GRID.index(0.95), sp.GRID.index(0.05)
        self.assertEqual(script.strict_hit(q, q[i95] + 0.01, 0.95), 1)
        self.assertEqual(script.strict_hit(q, q[i95], 0.95), 0)
        self.assertEqual(script.strict_hit(q, q[i05] - 0.01, 0.05), 1)
        self.assertEqual(script.strict_hit(q, q[i05], 0.05), 0)

    def test_the_ordinal_code_reproduces_the_strict_hits_at_the_four_levels(self):
        q = self.quantiles()
        rng = random.Random(9)
        for _ in range(500):
            y = rng.gauss(0, 2.2)
            u = script.ordinal_u(q, y)
            for level in script.LEVELS:
                coded = int(u > level) if level > 0.5 else int(u < level)
                self.assertEqual(coded, script.strict_hit(q, y, level), (y, level))


class SpacingTests(unittest.TestCase):
    def test_the_rows_kept_at_spacing_s_are_every_sth_by_global_order_within_the_regime(self):
        order = list(range(12))
        regimes = ["a"] * 5 + ["b"] * 7
        self.assertEqual(script.kept_rows(order, regimes, "a", 2), [0, 2, 4])
        self.assertEqual(script.kept_rows(order, regimes, "b", 2), [6, 8, 10])
        self.assertEqual(script.kept_rows(order, regimes, "b", 3), [6, 9])
        self.assertEqual(script.kept_rows(order, regimes, "a", 1), [0, 1, 2, 3, 4])


class LiftTests(unittest.TestCase):
    def test_hits_that_always_follow_hits_lift_above_one(self):
        hits = ([1, 1, 0, 0, 0, 0, 0, 0] * 30)
        pos = list(range(len(hits)))
        n11, exp = script.lift_terms(hits, ["r"] * len(hits), pos, 1)
        self.assertGreater(script.lift(n11, exp), 2.0)

    def test_an_alternating_sequence_has_no_lag_one_pairs(self):
        hits = [1, 0] * 50
        pos = list(range(len(hits)))
        n11, exp = script.lift_terms(hits, ["r"] * 100, pos, 1)
        self.assertEqual(sum(n11), 0)
        self.assertLess(script.lift(n11, exp), 0.01)

    def test_independent_draws_lift_about_one(self):
        rng = random.Random(4)
        hits = [int(rng.random() < 0.2) for _ in range(20000)]
        n11, exp = script.lift_terms(hits, ["r"] * len(hits), list(range(len(hits))), 3)
        self.assertAlmostEqual(script.lift(n11, exp), 1.0, delta=0.12)

    def test_a_pair_across_a_regime_or_a_gap_is_not_counted(self):
        hits = [1, 1, 1, 1]
        n11, exp = script.lift_terms(hits, ["a", "a", "b", "b"], [0, 1, 2, 3], 1)
        self.assertEqual(sum(n11), 2)  # (0,1) and (2,3); the pair (1,2) crosses a regime
        n11, exp = script.lift_terms(hits, ["a"] * 4, [0, 1, 5, 6], 1)
        self.assertEqual(sum(n11), 2)  # the pair (1, 5) is four panel days apart, not one

    def test_the_lift_uses_each_regimes_own_rate(self):
        # a rate of 1 in one regime and 0 in the other is not dependence: the expectation is taken regime by regime
        hits = [1] * 20 + [0] * 20
        n11, exp = script.lift_terms(hits, ["a"] * 20 + ["b"] * 20, list(range(40)), 1)
        self.assertAlmostEqual(script.lift(n11, exp), 1.0, places=9)


class RateFitTests(unittest.TestCase):
    def test_the_fit_recovers_group_rates_on_a_partition(self):
        rng = random.Random(2)
        a = [rng.random() < 0.5 for _ in range(3000)]
        hits = [int(rng.random() < (0.30 if x else 0.02)) for x in a]
        rates = script.fit_rates(hits, [a, [not x for x in a]])
        self.assertAlmostEqual(sum(r for r, x in zip(rates, a) if x) / sum(a), sum(h for h, x in zip(hits, a) if x) / sum(a), places=6)
        self.assertAlmostEqual(sum(rates), sum(hits), places=4)

    def test_adjacent_days_that_share_a_day_type_lift_less_once_the_rate_is_typed(self):
        # hits only on "calendar" days, which come in pairs of adjacent days: a regime-only lift is high, a typed lift is about one
        rng = random.Random(8)
        flag, hits = [], []
        for _ in range(4000):
            on = rng.random() < 0.1
            flag += [on, on]
            hits += [int(on and rng.random() < 0.3), int(on and rng.random() < 0.3)]
        n = len(hits)
        pos = list(range(n))
        plain = script.lift(*script.lift_terms(hits, ["r"] * n, pos, 1))
        rates = script.fit_rates(hits, [flag, [not x for x in flag]])
        typed = script.lift(*script.typed_lift_terms(hits, rates, ["r"] * n, pos, 1))
        self.assertGreater(plain, 1.5)
        self.assertAlmostEqual(typed, 1.0, delta=0.2)


class SpreadMeasureTests(unittest.TestCase):
    def test_the_mean_absolute_deviation_of_a_normal_forecast_is_its_expectation(self):
        q = [N.inv_cdf(level) * 2.0 for level in sp.GRID]
        got = script.mean_abs_dev(q)
        self.assertAlmostEqual(got, 2.0 * 0.7979, delta=0.08)

    def test_it_scales_with_the_spread_and_not_with_the_location(self):
        base = [N.inv_cdf(level) for level in sp.GRID]
        self.assertAlmostEqual(script.mean_abs_dev([3.0 * v + 5.0 for v in base]), 3.0 * script.mean_abs_dev(base), places=9)


class AdjustmentTests(unittest.TestCase):
    def frame(self, **kw):
        return script.Frame.from_window(script.load_window_doc(walk_doc(**kw)))

    def test_a_forecast_with_nothing_to_learn_is_left_alone_early_on(self):
        frame = self.frame(n_days=60)
        for variant in script.VARIANTS:
            adjusted = script.adjust(frame, variant)
            # fewer than 100 (A1) or 30 (A2) resolved cells in the first days: unchanged
            self.assertEqual(adjusted[0][1], frame.q[0][1], variant)

    def test_recentre_removes_a_level_the_forecast_misses(self):
        # the walk's forecast is shifted by -1.5; the public error carries it, the online slope learns to take it up
        frame = self.frame(n_days=900, phi=0.9, shift=0.0)
        shifted = script.Frame.shifted(frame, -1.5)
        base = sum(abs(shifted.y[i][1] - shifted.q[i][1][MED]) for i in range(len(shifted.days)))
        adjusted = script.adjust(shifted, "A1_recentre")
        after = sum(abs(shifted.y[i][1] - adjusted[i][1][MED]) for i in range(len(shifted.days)))
        self.assertLess(after, base)

    def test_rescale_widens_a_forecast_that_is_too_narrow_and_clamps(self):
        frame = script.Frame.scaled(self.frame(n_days=900, phi=0.0), 0.5)
        adjusted = script.adjust(frame, "A2_rescale")
        late = len(frame.days) - 1
        before = frame.q[late][1][-1] - frame.q[late][1][0]
        after = adjusted[late][1][-1] - adjusted[late][1][0]
        self.assertGreater(after, 1.4 * before)  # the forecast is half as wide as the data: the ratio is about 2, clamped at 1.5
        self.assertLessEqual(after, script.KAPPA_CLAMP[1] * before * (1 + 1e-9))

    def test_a_negative_public_error_slope_is_taken_up_only_by_the_variant_that_allows_it(self):
        # an ignorant forecast (median 0) of a spread with y_t = -0.6 y_(t-2) + noise: the public error predicts the target's with a negative sign
        doc = walk_doc(n_days=700, phi=0.0)
        rng = random.Random(6)
        cal = doc["calendar"]
        y = {}
        for i, d in enumerate(cal):
            y[d] = rng.gauss(0, 1) - (0.6 * y[cal[i - 2]] if i >= 2 else 0.0)
        for t in doc["outcome"]:
            doc["outcome"][t] = y[t]
        doc["models"][script.CANDIDATE] = [[N.inv_cdf(level) for level in sp.GRID] for _ in doc["cells"]]
        frame = script.Frame.from_window(script.load_window_doc(doc))
        a1 = script.adjust(frame, "A1_recentre")
        a4 = script.adjust(frame, "A4_meanrevert")
        self.assertEqual(a1[-1][1], frame.q[-1][1])  # beta clamped at zero
        self.assertNotEqual(a4[-1][1], frame.q[-1][1])

    def test_an_adjusted_forecast_keeps_its_quantiles_ordered(self):
        frame = self.frame(n_days=400, phi=0.8)
        for variant in script.VARIANTS:
            for row in script.adjust(frame, variant):
                for h in sp.HORIZONS:
                    q = row[h]
                    self.assertTrue(all(a <= b for a, b in zip(q, q[1:])), variant)

    def test_the_constants_are_the_declarations(self):
        a = DECLARATION["adjustments"]
        self.assertEqual(script.MIN_RESOLVED_A1, 100)
        self.assertEqual(script.MIN_RESOLVED_A2, 30)
        self.assertEqual(script.WINDOW_A2, 60)
        self.assertEqual((script.WINDOW_A5, script.MIN_RESOLVED_A5), (20, 10))
        self.assertEqual(script.BETA_CLAMP_A4, (-1.0, 1.0))
        self.assertEqual(script.KAPPA_CLAMP, (0.7, 1.5))
        self.assertEqual(script.BETA_CLAMP, (0.0, 1.0))
        self.assertEqual(len(script.VARIANTS), a["variant_count"])
        self.assertEqual(script.SEED, 1523)
        self.assertEqual(script.REPS, 2000)
        self.assertEqual(sorted(DECLARATION["variants"]), sorted(("sc_s3c_ann_net",) + tuple(script.VARIANTS)))
        self.assertEqual(len(DECLARATION["amendments"]), 1)


class GuardTests(unittest.TestCase):
    """The online rules read only outcomes that are public at the decision day: the target's panel day is at most D - 1."""

    def test_a_target_that_is_not_public_is_refused(self):
        with self.assertRaises(LookAheadError):
            script.require_public(target_pos=10, decision_pos=10)
        with self.assertRaises(LookAheadError):
            script.require_public(target_pos=11, decision_pos=10)
        script.require_public(target_pos=9, decision_pos=10)

    def test_the_resolved_cells_of_a_lead_stop_at_the_day_before_the_decision(self):
        # decision positions 5..9, lead h = 2: the cell of decision position p has its target at p + 2
        positions = [5, 6, 7, 8, 9]
        # targets 7..11; the bound is target_pos <= decision_pos - 1 = 8: targets 7 (p = 5) and 8 (p = 6)
        self.assertEqual(script.public_resolved(positions, 2, decision_pos=9), [0, 1])

    def test_an_outcome_not_yet_public_never_moves_the_adjusted_forecast(self):
        doc = walk_doc(n_days=260, phi=0.8, shift=-1.0)
        frame = script.Frame.from_window(script.load_window_doc(doc))
        for variant in script.VARIANTS:
            base = script.adjust(frame, variant)
            for i in (150, 200):
                decision_pos = frame.pos[i]
                changed = json.loads(json.dumps(doc))
                # change every outcome on a panel day at or after the decision day: none is public when decision i is made
                for t in list(changed["outcome"]):
                    if changed["calendar"].index(t) >= decision_pos:
                        changed["outcome"][t] += 50.0
                other = script.adjust(script.Frame.from_window(script.load_window_doc(changed)), variant)
                self.assertEqual(other[i], base[i], (variant, i))


class SimulationTests(unittest.TestCase):
    def test_a_calibrated_forecaster_with_the_information_lag_shows_lag_one_dependence(self):
        lagged = script.simulate_path(phi=0.9, n=3000, lag=1, seed=11, leads=(1,))
        control = script.simulate_path(phi=0.9, n=3000, lag=0, seed=11, leads=(1,))
        self.assertGreater(lagged["lift"][1][1], 2.0)
        self.assertLess(control["lift"][1][1], 2.0)

    def test_spacing_h_reads_the_shared_innovation_and_spacing_h_plus_one_does_not(self):
        rejects_h, rejects_h1 = 0, 0
        for seed in range(30):
            r = script.simulate_path(phi=0.9, n=1855, lag=1, seed=seed, leads=(1,))
            rejects_h += r["independence_p"][1][0] < 0.05
            rejects_h1 += r["independence_p"][1][1] < 0.05
        self.assertGreater(rejects_h, 20)
        self.assertLess(rejects_h1, 9)

    def test_the_simulation_is_deterministic(self):
        a = script.simulate_path(phi=0.6, n=400, lag=1, seed=5, leads=(1, 2))
        b = script.simulate_path(phi=0.6, n=400, lag=1, seed=5, leads=(1, 2))
        self.assertEqual(a, b)


class WindowTests(unittest.TestCase):
    def test_a_day_after_the_last_development_day_is_refused(self):
        doc = walk_doc(n_days=30)
        doc["calendar"] = doc["calendar"] + ["2026-01-06"]
        doc["cells"].append(["2025-12-31", 1, "2026-01-06"])
        doc["outcome"]["2026-01-06"] = 0.0
        doc["targets"]["2026-01-06"] = {"regime": "r", "types": ["ordinary"], "pressure": "ordinary"}
        doc["models"][script.CANDIDATE].append([0.0] * len(sp.GRID))
        with self.assertRaises(LookAheadError):
            script.load_window_doc(doc)

    def test_another_window_is_refused(self):
        doc = walk_doc(n_days=30)
        doc["window"] = "2026"
        with self.assertRaises(ValueError):
            script.load_window_doc(doc)

    def test_the_requirement_flag_stays_off_in_the_tree(self):
        self.assertFalse(sp.COVERAGE_REQUIREMENT_IN_FORCE)


if __name__ == "__main__":
    unittest.main()
