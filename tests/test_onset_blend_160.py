"""The onset-day blend candidate (#160): `scripts/onset_blend_160.py`.

The test is declared in `docs/pivot/onset-blend-160.md` before any scoring. These tests check the pure
pieces: the blend, the pass rule, and the refusal to score a day from 2026-01-01.

Recorded mutation (CLAUDE.md, a leakage guard): changing `if day >= TEST_END:` in `require_before_2026` to
`if day > TEST_END:` makes `OnsetBlendTests.test_a_day_from_2026_is_refused` fail with
`AssertionError: LookAheadError not raised`.
"""

from __future__ import annotations

import importlib.util
import unittest
from datetime import date
from pathlib import Path

from repo_model.splits import LookAheadError

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "onset_blend_160.py"


def _load():
    spec = importlib.util.spec_from_file_location("onset_blend_160", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _cell(days, lower, upper, mean=0.0):
    return {"days": days, "mean": mean, "interval": {"lower": lower, "upper": upper}}


class OnsetBlendTests(unittest.TestCase):
    def setUp(self):
        self.m = _load()

    def test_blend_is_the_unweighted_mean(self):
        self.assertEqual(self.m.blend([0.0, 0.5, 1.0], [0.2, 0.5, 0.0]), [0.1, 0.5, 0.5])

    def test_blend_refuses_unequal_lengths(self):
        with self.assertRaises(ValueError):
            self.m.blend([0.1], [0.1, 0.2])

    def test_a_day_from_2026_is_refused(self):
        with self.assertRaises(LookAheadError):
            self.m.require_before_2026([date(2025, 12, 31), date(2026, 1, 1)])
        self.m.require_before_2026([date(2025, 12, 31)])

    def test_pass_needs_lower_bound_above_zero_at_both_thresholds(self):
        cells = {"5": {"all": _cell(100, 0.001, 0.004)}, "10": {"all": _cell(100, -0.0001, 0.004)}}
        self.assertFalse(self.m.judge(cells)["passes"])
        cells["10"]["all"] = _cell(100, 0.0001, 0.004)
        self.assertTrue(self.m.judge(cells)["passes"])

    def test_a_cell_worse_beyond_its_interval_fails_the_test(self):
        cells = {t: {"all": _cell(100, 0.001, 0.004), "regime 2024": _cell(50, -0.003, -0.001)} for t in ("5", "10")}
        verdict = self.m.judge(cells)
        self.assertFalse(verdict["passes"])
        self.assertIn("regime 2024", verdict["worse_cells"]["5"])

    def test_a_cell_under_20_days_is_not_judged(self):
        cells = {t: {"all": _cell(100, 0.001, 0.004), "day type tax_date": _cell(19, -0.003, -0.001)} for t in ("5", "10")}
        self.assertTrue(self.m.judge(cells)["passes"])


if __name__ == "__main__":
    unittest.main()
