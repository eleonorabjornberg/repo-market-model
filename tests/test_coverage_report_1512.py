"""The amendment 4 coverage report for (s3c-ann-net) (#1512): `scripts/coverage_report_1512.py`.

The tests fix the arithmetic on hand cases: the tie probability read from a 23-quantile forecast, the deterministic draws, how a walk
file becomes the inputs of `scoring_protocol.coverage_cells`, that the per-cell pass/fail the report prints is the one
`enforce_coverage_requirement` reads (the flag patched on inside the call only; in the tree it stays False), and the guard the report adds:
it reads the development window only and refuses a walk file with a day after 2025-12-31 or a locked day.

**Recorded mutation (development window only).** In `coverage_report_1512.load_window`, deleting the `m63.refuse_beyond(...)` call fails
`WindowGuardTests.test_a_day_after_the_development_window_is_refused` with `AssertionError: LookAheadError not raised`.
"""

from __future__ import annotations

import importlib.util
import json
import sys
import unittest
from datetime import date, timedelta
from pathlib import Path
from unittest import mock

REPO = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("coverage_report_1512_script", REPO / "scripts" / "coverage_report_1512.py")
script = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = script
spec.loader.exec_module(script)

from repo_model import coverage_tests as ct  # noqa: E402
from repo_model import scoring_protocol as sp  # noqa: E402
from repo_model.splits import LookAheadError  # noqa: E402


def business_days(count, start=date(2018, 4, 3)):
    days, day = [], start
    while len(days) < count:
        if day.weekday() < 5:
            days.append(day)
        day += timedelta(days=1)
    return days


def law(centre=0.0, width=10.0):
    return [centre + (level - 0.5) * width for level in sp.GRID]


def doc(n=120, name="development", start=date(2018, 4, 3), outcome=lambda i: 0.0):
    """A tiny walk file: n decision days, two regimes, one forecast law for every cell."""

    calendar = business_days(n + 6, start)
    cells, outcomes, targets, regimes = [], {}, {}, {}
    for i in range(n):
        regimes[calendar[i].isoformat()] = "calm" if i < n // 2 else "stress"
        for h in sp.HORIZONS:
            t = calendar[i + h]
            cells.append([calendar[i].isoformat(), h, t.isoformat()])
            outcomes[t.isoformat()] = outcome(i + h)
            targets[t.isoformat()] = {"regime": "x", "types": ["ordinary"], "pressure": "ordinary"}
    return {
        "window": name, "instant": "18:00", "panel_sha256": "x", "declaration": 1363,
        "calendar": [d.isoformat() for d in calendar], "cells": cells, "outcome": outcomes, "targets": targets,
        "regime_of_day": regimes, "refits": 1,
        "models": {script.CANDIDATE: [law() for _ in cells]},
    }


class TieProbabilityTests(unittest.TestCase):
    def test_distinct_quantiles_give_the_bracket_between_neighbours(self):
        probs = script.tie_probabilities(law())
        # q95 sits between q90 (0.90) and q975 (0.975)? the grid's neighbours bound the bracket; the upper-tail need is at - tau
        index = sp.GRID.index(0.95)
        below, at = sp.GRID[index - 1], sp.GRID[index + 1]
        self.assertAlmostEqual(probs[index], (at - 0.95) / (at - below))
        index = sp.GRID.index(0.05)
        below, at = sp.GRID[index - 1], sp.GRID[index + 1]
        self.assertAlmostEqual(probs[index], (0.05 - below) / (at - below))

    def test_a_flat_run_of_quantiles_spreads_the_tie_over_the_mass(self):
        flat = law()
        k = sp.GRID.index(0.95)
        flat[k - 1] = flat[k] = flat[k + 1] = flat[k]  # q90, q95, q975 all equal
        probs = script.tie_probabilities(flat)
        below, at = sp.GRID[k - 2], sp.GRID[k + 2]
        self.assertAlmostEqual(probs[k], (at - 0.95) / (at - below))
        self.assertTrue(all(0.0 <= p <= 1.0 for p in probs))

    def test_every_value_is_accepted_by_the_protocol_hit_rule(self):
        probs = script.tie_probabilities(law())
        for level in sp.COVERAGE_LEVELS:
            ct.randomised_hit_sequence([0.0], [0.0], [probs[sp.GRID.index(level)]], [0.5])


class DrawTests(unittest.TestCase):
    def test_draws_are_deterministic_and_in_range(self):
        w = script.load_window_doc(doc(30))
        a, b = script.make_draws(w), script.make_draws(w)
        self.assertEqual(a, b)
        self.assertEqual(set(a), set(w.days))
        self.assertTrue(all(0.0 <= u < 1.0 for d in a.values() for h in d.values() for u in h))
        self.assertEqual(len(next(iter(a.values()))[1]), len(sp.GRID))


class InputsTests(unittest.TestCase):
    def test_inputs_are_the_cells_of_the_walk(self):
        w = script.load_window_doc(doc(40))
        inp = script.inputs(w)
        self.assertEqual(sorted(inp["forecasts"]), w.days)
        self.assertEqual(set(inp["forecasts"][w.days[0]]), set(sp.HORIZONS))
        self.assertEqual(inp["regimes"][w.days[0]], "calm")
        self.assertEqual(inp["regimes"][w.days[-1]], "stress")

    def test_a_target_that_is_not_the_hth_calendar_day_is_refused(self):
        d = doc(40)
        d["cells"][0][2] = d["cells"][1][2]  # lead 1 now targets lead 2's day
        w = script.load_window_doc(d)
        with self.assertRaises(ValueError):
            script.inputs(w)


class WindowGuardTests(unittest.TestCase):
    def test_a_day_after_the_development_window_is_refused(self):
        late = doc(40, start=date(2025, 11, 3))  # targets run into 2026
        with self.assertRaises(LookAheadError):
            script.load_window_doc(late)

    def test_another_window_is_refused(self):
        with self.assertRaises(ValueError):
            script.load_window_doc(doc(40, name="2026"))

    def test_a_locked_day_is_refused(self):
        blind = doc(40, start=date(2026, 9, 7))
        blind["window"] = "development"
        with self.assertRaises(LookAheadError):
            script.load_window_doc(blind)


class ReportTests(unittest.TestCase):
    def setUp(self):
        self.w = script.load_window_doc(doc(150))

    def test_the_cells_carry_three_rules_and_four_levels(self):
        rep = script.report(self.w)
        self.assertEqual({c["rule"] for c in rep["cells"]}, {"strict", "tie_counts", "randomised"})
        self.assertEqual({c["level"] for c in rep["cells"]}, {0.01, 0.05, 0.95, 0.99})
        self.assertEqual({c["lead"] for c in rep["cells"]}, set(sp.HORIZONS))
        self.assertEqual({c["regime"] for c in rep["cells"]}, {"calm", "stress"})
        self.assertEqual(rep["method"], "thinned")
        self.assertEqual(rep["family"], "holm")
        self.assertEqual(rep["alpha"], 0.05)

    def test_the_flag_stays_off_in_the_tree(self):
        script.report(self.w)
        self.assertFalse(sp.COVERAGE_REQUIREMENT_IN_FORCE)

    def test_a_forecast_far_too_narrow_fails_every_rule(self):
        d = doc(300, outcome=lambda i: 40.0 if i % 3 else -40.0)
        rep = script.report(script.load_window_doc(d))
        for rule in ("strict", "tie_counts", "randomised"):
            self.assertFalse(rep["verdict"][rule]["passes"], rule)
            self.assertTrue(rep["verdict"][rule]["failing_tests"])

    def test_the_report_verdict_is_what_enforce_would_read(self):
        # both directions: a world that fails, and one that passes, agree with enforce_coverage_requirement itself
        for outcome in (lambda i: 40.0 if i % 3 else -40.0, lambda i: ((i * 7919) % 1000) / 100.0 - 5.0):
            rep = script.report(script.load_window_doc(doc(300, outcome=outcome)))
            cells = rep["_cells"]
            for rule in ("strict", "tie_counts", "randomised"):
                with mock.patch.object(sp, "COVERAGE_REQUIREMENT_IN_FORCE", True):
                    try:
                        sp.enforce_coverage_requirement(cells, alpha=0.05, family="holm", rule=rule)
                        enforce = True
                    except sp.CoverageRequirementFailed:
                        enforce = False
                self.assertEqual(rep["verdict"][rule]["passes"], enforce, rule)

    def test_a_cell_passes_only_when_none_of_its_tests_is_rejected(self):
        d = doc(300, outcome=lambda i: 40.0 if i % 3 else -40.0)
        rep = script.report(script.load_window_doc(d))
        table = rep["pass_fail"]["strict"]
        self.assertEqual(set(table), {str(h) for h in sp.HORIZONS})
        self.assertFalse(any(table["1"][regime] for regime in ("calm", "stress")))

    def test_result_is_json(self):
        rep = script.report(self.w)
        json.dumps({k: v for k, v in rep.items() if not k.startswith("_")})


class DeclaredDesignTests(unittest.TestCase):
    def test_the_design_is_the_amendments_answers(self):
        self.assertEqual((script.METHOD, script.FAMILY, script.ALPHA), ("thinned", "holm", 0.05))
        self.assertEqual(script.RULES, ("strict", "tie_counts", "randomised"))
        self.assertEqual(script.LAST_DAY, date(2025, 12, 31))


if __name__ == "__main__":
    unittest.main()
