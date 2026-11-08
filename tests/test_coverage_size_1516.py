"""The helpers of `scripts/coverage_size_1516.py` (#1516; H5, step M5 registration, development tier).

The study measures the empirical size of the amendment 4 coverage design (Kupiec and Christoffersen at q05/q95 and q01/q99, leads 1 to 5,
each regime, thinned days above lead 1, Holm over the family at 5%) on hit sequences that are calibrated by construction but keep the
serial structure of the candidate (s3c-ann-net)'s own development forecasts, beside the same design with a Newey-West (HAC) Kupiec. It
adds no scoring rule and changes no threshold. What these tests pin:

- the study's fast engine gives exactly the p-values of `scoring_protocol.coverage_cells` (method "thinned" and method "hac") on a world
  with continuous outcomes, so the size it reports is the size of the amendment's design and not of a lookalike;
- its Holm step-down rejects what `scoring_protocol.holm` rejects;
- the randomised PIT lies in its bracket, the rank transform makes a calibrated margin, and the stationary bootstrap is a valid index
  sequence (one block length of 1 is a plain resample, a very long one is a run of consecutive days);
- in a world with no serial structure the design's Kupiec test has about its nominal size (a loose, seeded bound);
- the window guard: the study reads the development window only and refuses a decision or target day after 2025-12-31.

Recorded mutation for the window guard (a new leakage guard): deleting the `m63.refuse_beyond(...)` call in `load_window_doc` makes
`WindowGuardTests.test_a_day_after_the_last_development_day_is_refused` fail with `AssertionError: LookAheadError not raised`.
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
_spec = importlib.util.spec_from_file_location("coverage_size_1516", ROOT / "scripts" / "coverage_size_1516.py")
script = importlib.util.module_from_spec(_spec)
sys.modules["coverage_size_1516"] = script  # the script's worker pool pickles its functions by module name
_spec.loader.exec_module(script)

N = NormalDist()


def business_days(start: date, n: int):
    out, d = [], start
    while len(out) < n:
        if d.weekday() < 5:
            out.append(d)
        d += timedelta(days=1)
    return out


def world(n_days: int = 150, seed: int = 7, dependent: bool = True):
    """A calendar, 23-quantile forecasts of a continuous latent, outcomes, and three regimes; serially dependent errors when asked."""

    rng = random.Random(seed)
    calendar = business_days(date(2019, 3, 4), n_days + 12)
    err, prev = {}, 0.0
    for d in calendar:
        prev = (0.7 * prev + rng.gauss(0, 1)) if dependent else rng.gauss(0, 1)
        err[d] = prev
    outcomes = {d: err[d] for d in calendar}
    decisions = calendar[:n_days]
    regimes = {d: ("a" if i < n_days // 3 else "b" if i < 2 * n_days // 3 else "c") for i, d in enumerate(decisions)}
    forecasts = {}
    for d in decisions:
        # a fixed, slightly off forecast law per lead: quantiles of N(0, sd_h)
        forecasts[d] = {h: [N.inv_cdf(level) * (0.9 + 0.1 * h) for level in sp.GRID] for h in sp.HORIZONS}
    return forecasts, outcomes, calendar, regimes


class HolmTests(unittest.TestCase):
    def test_the_step_down_count_is_the_protocols(self):
        rng = random.Random(1)
        for _ in range(300):
            m = rng.randint(1, 40)
            ps = [rng.random() ** rng.choice((1, 3, 6)) for _ in range(m)]
            mine = script.holm_rejections(ps, 0.05)
            theirs = sum(sp.holm({str(i): p for i, p in enumerate(ps)}, 0.05).values())
            self.assertEqual(mine, theirs)

    def test_hand_cases(self):
        self.assertEqual(script.holm_rejections([0.001, 0.2, 0.5], 0.05), 1)
        self.assertEqual(script.holm_rejections([0.5, 0.2], 0.05), 0)
        self.assertEqual(script.holm_rejections([0.001, 0.01, 0.02], 0.05), 3)


class PitTests(unittest.TestCase):
    def test_the_pit_lies_in_the_bracket_of_the_outcome(self):
        q = [N.inv_cdf(l) for l in sp.GRID]
        for y in (-3.0, -1.0, 0.0, 0.3, 2.5):
            below = max([l for l, v in zip(sp.GRID, q) if v < y], default=0.0)
            above = min([l for l, v in zip(sp.GRID, q) if v > y], default=1.0)
            for r in (0.0, 0.5, 0.999):
                u = script.randomised_pit(q, y, r)
                self.assertGreaterEqual(u, below)
                self.assertLessEqual(u, above)

    def test_beyond_the_tails_the_pit_is_in_the_end_brackets(self):
        q = [N.inv_cdf(l) for l in sp.GRID]
        self.assertLess(script.randomised_pit(q, q[0] - 1.0, 0.5), sp.GRID[0])
        self.assertGreater(script.randomised_pit(q, q[-1] + 1.0, 0.5), sp.GRID[-1])

    def test_a_strict_hit_is_a_pit_beyond_the_level(self):
        q = [N.inv_cdf(l) for l in sp.GRID]
        i95 = sp.GRID.index(0.95)
        self.assertGreater(script.randomised_pit(q, q[i95] + 0.01, 0.0), 0.95)
        self.assertLess(script.randomised_pit(q, q[i95] - 0.01, 0.999), 0.95)


class RankAndBootstrapTests(unittest.TestCase):
    def test_rank_uniform_is_a_calibrated_margin_and_keeps_order(self):
        xs = [0.9, 0.1, 0.5, 0.7, 0.3]
        v = script.rank_uniform(xs)
        self.assertEqual(sorted(v), [1 / 6, 2 / 6, 3 / 6, 4 / 6, 5 / 6])
        self.assertEqual([x < y for x, y in zip(xs, xs[1:])], [a < b for a, b in zip(v, v[1:])])

    def test_indices_are_in_range_and_of_the_right_length(self):
        rng = random.Random(3)
        for n, block in ((1, 10.0), (7, 1.0), (50, 10.0), (200, 25.0)):
            idx = script.stationary_indices(n, block, rng)
            self.assertEqual(len(idx), n)
            self.assertTrue(all(0 <= i < n for i in idx))

    def test_a_very_long_block_is_a_run_of_consecutive_days(self):
        idx = script.stationary_indices(40, 1e9, random.Random(5))
        self.assertTrue(all(b == (a + 1) % 40 for a, b in zip(idx, idx[1:])))

    def test_a_block_of_one_is_mostly_not_consecutive(self):
        idx = script.stationary_indices(2000, 1.0, random.Random(5))
        consecutive = sum(1 for a, b in zip(idx, idx[1:]) if b == (a + 1) % 2000)
        self.assertLess(consecutive, 100)

    def test_the_mean_block_length_is_respected(self):
        idx = script.stationary_indices(20000, 10.0, random.Random(5))
        starts = 1 + sum(1 for a, b in zip(idx, idx[1:]) if b != (a + 1) % 20000)
        self.assertGreater(20000 / starts, 8.0)
        self.assertLess(20000 / starts, 12.5)


class EngineTests(unittest.TestCase):
    """The engine gives `coverage_cells`' p-values: the size it measures is the amendment's design."""

    def check(self, dependent: bool, seed: int):
        forecasts, outcomes, calendar, regimes = world(seed=seed, dependent=dependent)
        sample = script.sample_from_forecasts(forecasts, outcomes, calendar, regimes, seed=11)
        mine = script.cell_p_values(sample, sample.u)
        for method in ("thinned", "hac"):
            cells = sp.coverage_cells(forecasts, outcomes, calendar, regimes, method=method)
            seen = 0
            for c in cells:
                if c.rule != "strict":
                    continue
                kup_iid, kup_hac, ind = mine[(c.lead, c.regime, c.level)]
                self.assertAlmostEqual(c.kupiec_p, kup_iid if method == "thinned" else kup_hac, places=12, msg=c.label())
                if c.independence_p is None:
                    self.assertIsNone(ind)
                else:
                    self.assertAlmostEqual(c.independence_p, ind, places=12, msg=c.label())
                seen += 1
            self.assertEqual(seen, len(mine))

    def test_equal_to_coverage_cells_on_dependent_errors(self):
        self.check(True, 7)

    def test_equal_to_coverage_cells_on_independent_errors(self):
        self.check(False, 8)

    def test_the_hit_counts_of_the_pit_are_the_hit_counts_of_the_outcomes(self):
        forecasts, outcomes, calendar, regimes = world()
        sample = script.sample_from_forecasts(forecasts, outcomes, calendar, regimes, seed=3)
        cells = {(c.lead, c.regime, c.level): c for c in sp.coverage_cells(forecasts, outcomes, calendar, regimes, method="thinned") if c.rule == "strict"}
        for (h, regime, level), hits in script.thinned_hit_counts(sample, sample.u).items():
            self.assertEqual(hits, cells[(h, regime, level)].hits)

    def test_the_family_has_one_hundred_cells_in_five_regimes(self):
        # 5 leads x r regimes x 4 levels; this world has 3 regimes
        forecasts, outcomes, calendar, regimes = world()
        sample = script.sample_from_forecasts(forecasts, outcomes, calendar, regimes, seed=3)
        self.assertEqual(len(script.cell_p_values(sample, sample.u)), 5 * 3 * 4)


class NullWorldTests(unittest.TestCase):
    def setUp(self):
        forecasts, outcomes, calendar, regimes = world(n_days=240, dependent=True)
        self.sample = script.sample_from_forecasts(forecasts, outcomes, calendar, regimes, seed=3)

    def test_a_null_margin_is_uniform_within_each_regime_and_lead(self):
        v = script.null_world(self.sample, "bootstrap", 10.0, random.Random(1))
        for h in sp.HORIZONS:
            for regime in set(self.sample.regimes):
                idx = [i for i, r in enumerate(self.sample.regimes) if r == regime]
                grid = sorted(v[h][i] for i in idx)
                self.assertTrue(all(0.0 < x < 1.0 for x in grid))
                # a resample of the ranks of the regime: every value is one of the regime's rank values
                n = len(idx)
                allowed = {k / (n + 1) for k in range(1, n + 1)}
                self.assertTrue(all(any(abs(x - a) < 1e-12 for a in allowed) for x in grid[:5]))

    def test_the_bootstrap_moves_whole_days_across_leads(self):
        v = script.null_world(self.sample, "bootstrap", 10.0, random.Random(1))
        u = self.sample.u
        # the cross-lead rank pattern of a resampled day is the pattern of some original day of the same regime
        n = len(self.sample.days)
        table = {tuple(round(script.rank_uniform_of(self.sample, h)[j], 12) for h in sp.HORIZONS) for j in range(n)}
        for i in range(0, n, 17):
            self.assertIn(tuple(round(v[h][i], 12) for h in sp.HORIZONS), table)

    def test_the_iid_control_has_no_structure_and_is_seeded(self):
        a = script.null_world(self.sample, "iid", 10.0, random.Random(1))
        b = script.null_world(self.sample, "iid", 10.0, random.Random(1))
        self.assertEqual(a, b)
        self.assertNotEqual(a, script.null_world(self.sample, "iid", 10.0, random.Random(2)))

    def test_an_unknown_world_is_refused(self):
        with self.assertRaises(ValueError):
            script.null_world(self.sample, "nope", 10.0, random.Random(1))

    def test_kupiec_has_about_its_nominal_size_in_the_iid_control(self):
        rng = random.Random(2024)
        reject = total = 0
        for _ in range(60):
            v = script.null_world(self.sample, "iid", 10.0, rng)
            for key, (kup_iid, _hac, _ind) in script.cell_p_values(self.sample, v).items():
                total += 1
                reject += kup_iid < 0.05
        self.assertLess(reject / total, 0.09)
        self.assertGreater(reject / total, 0.02)


class WindowGuardTests(unittest.TestCase):
    def doc(self, last: str = "2025-12-30"):
        d0 = date.fromisoformat(last) - timedelta(days=5)
        days = [d0 + timedelta(days=i) for i in range(5)]
        t = date.fromisoformat(last)
        return {
            "window": "development", "calendar": [x.isoformat() for x in days + [t]],
            "cells": [[days[0].isoformat(), 1, t.isoformat()]], "outcome": {t.isoformat(): 1.0},
            "targets": {t.isoformat(): {"regime": "r", "types": ["ordinary"], "pressure": "p"}},
            "regime_of_day": {days[0].isoformat(): "r"},
            "models": {script.CANDIDATE: [[0.0] * len(sp.GRID)]},
        }

    def test_the_development_window_is_read(self):
        window = script.load_window_doc(self.doc())
        self.assertEqual(window.name, "development")

    def test_another_window_is_refused(self):
        doc = self.doc()
        doc["window"] = "2026"
        with self.assertRaises(ValueError):
            script.load_window_doc(doc)

    def test_a_day_after_the_last_development_day_is_refused(self):
        with self.assertRaises(LookAheadError):
            script.load_window_doc(self.doc("2026-01-06"))


class HacZeroHitTests(unittest.TestCase):
    def test_a_cell_with_no_hit_is_rejected_outright_by_the_hac_kupiec(self):
        # the variance is centred at the nominal rate: zero hits give a variance of about p^2 and a statistic of about n
        for n, lag in ((100, 0), (360, 0), (360, 4)):
            self.assertLess(sp._hac_kupiec_p([0] * n, 0.01, lag), 1e-4)
        self.assertGreater(sp._hac_kupiec_p([0] * 99 + [1], 0.01, 0), 0.5)


class FlagTests(unittest.TestCase):
    def test_the_requirement_flag_stays_off_in_the_tree(self):
        self.assertFalse(sp.COVERAGE_REQUIREMENT_IN_FORCE)


class PageTests(unittest.TestCase):
    def test_the_committed_page_is_what_the_committed_record_gives(self):
        record = ROOT / "docs" / "research" / "coverage-size-1516" / "result.json"
        page = ROOT / "docs" / "research" / "coverage-size-1516-result.md"
        if not record.exists():
            self.skipTest("the record is written by the study's score step")
        r = json.loads(record.read_text(encoding="utf-8"))
        self.assertEqual(script.render(r), page.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
