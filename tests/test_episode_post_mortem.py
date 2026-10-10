"""The episode post-mortem (#474): `scripts/episode_post_mortem.py`.

Descriptive only: these tests check the readings it makes on small series with known answers,
and that it reads inputs as of the decision instant and refuses a locked day. They test no claim.

Recorded mutations (CLAUDE.md: each new leakage or availability guard carries one that kills it).

* `require_scored_days` refuses a locked or post-declared scored day. Mutation: delete the
  `require_unlocked(days, where="episode_post_mortem.require_scored_days")` line; the failing test
  was `GuardTests.test_a_locked_scored_day_is_refused`, which raised `AssertionError`
  (`"locked" does not match` the later-day message that remained). Mutation: replace `if late:` with `if False:`; the failing test was
  `GuardTests.test_a_day_after_the_last_scored_day_is_refused`, same exception.
* The inputs are read as of the decision instant. Mutation: in `as_of_series` replace
  `source = rows[reads[name].row]` with `source = rows[fold.index]`; the failing test was
  `GuardTests.test_an_input_is_read_from_before_the_scored_day`, which raised `AssertionError`
  (the scored day's own sentinel read back).
* The scale of `moved` is formed from changes that closed before the window opened. Mutation:
  replace `series[max(0, index - lag - trailing) : index - lag + 1]` with
  `series[max(0, index - trailing) : index + 1]`; the failing test was
  `MovedTests.test_the_scale_ignores_the_window_itself`, which raised `AssertionError`.
"""

from __future__ import annotations

import importlib.util
import math
import unittest
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _script(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


pm = _script("episode_post_mortem")


def _hz(p, c):
    return {"probability": p, "cutoff": c}


class ReadingTests(unittest.TestCase):
    def test_flag_is_at_or_above_the_cutoff_and_infinity_flags_nothing(self):
        self.assertTrue(pm.flagged(0.2, 0.2))
        self.assertFalse(pm.flagged(0.19, 0.2))
        self.assertFalse(pm.flagged(1.0, math.inf))

    def test_under_ratio_is_zero_when_nothing_can_be_flagged(self):
        self.assertEqual(pm.under_ratio(0.5, math.inf), 0.0)
        self.assertAlmostEqual(pm.under_ratio(0.1, 0.4), 0.25)

    def test_cause_precedence(self):
        near = {1: _hz(0.15, 0.2), 2: _hz(0.0, 0.2)}
        far = {1: _hz(0.01, 0.2), 2: _hz(0.0, math.inf)}
        self.assertEqual(pm.classify_miss(near, [True, True]), pm.CAUSE_UNDER)
        self.assertEqual(pm.classify_miss(far, [False, True]), pm.CAUSE_LATE)
        self.assertEqual(pm.classify_miss(far, [False, False]), pm.CAUSE_NONE)

    def test_the_best_cause_follows_the_declared_order(self):
        self.assertEqual(pm.best_cause([pm.CAUSE_NONE, pm.CAUSE_LATE]), pm.CAUSE_LATE)
        self.assertEqual(pm.best_cause([pm.CAUSE_NONE, pm.CAUSE_UNDER, pm.CAUSE_LATE]), pm.CAUSE_UNDER)

    def test_separates_needs_enough_others_and_a_level_outside_their_range(self):
        others = [1.0, 2.0, 3.0, 2.5, 1.5]
        self.assertTrue(pm.separates(4.0, others))
        self.assertFalse(pm.separates(2.0, others))
        self.assertFalse(pm.separates(9.0, others[:4]))
        self.assertFalse(pm.separates(None, others))


class MovedTests(unittest.TestCase):
    def _series(self):
        # 300 days alternating small noise, then a jump over the last 10 days.
        state, base = 12345, []
        for _ in range(300):
            state = (1103515245 * state + 12345) % (2**31)
            base.append(state / 2**31)
        return base

    def test_a_jump_over_the_window_moves(self):
        s = self._series()
        for i in range(290, 300):
            s[i] += 5.0 * (i - 289) / 10
        out = pm.moved(s, 299)
        self.assertTrue(out["moved"])
        self.assertGreater(out["standardised"], pm.MOVE_Z)

    def test_a_quiet_window_does_not_move(self):
        self.assertFalse(pm.moved(self._series(), 299)["moved"])

    def test_missing_values_read_as_not_moved(self):
        s = self._series()
        s[299] = None
        self.assertEqual(pm.moved(s, 299)["change"], None)
        self.assertFalse(pm.moved(s, 299)["moved"])

    def test_the_scale_ignores_the_window_itself(self):
        # The same history up to the window; two different windows must give the same scale.
        a = self._series()
        b = list(a)
        for i in range(290, 300):
            b[i] += 50.0
        self.assertEqual(pm.moved(a, 299)["scale"], pm.moved(b, 299)["scale"])

    def test_a_short_history_has_no_scale(self):
        out = pm.moved([0.0] * 5 + [1.0] * 10, 14)
        self.assertIsNone(out["standardised"])
        self.assertFalse(out["moved"])


class GuardTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import tempfile

        from repo_model.scarcity import measurement_declaration, with_reserve_scarcity_state

        validation = _script("scarcity_validation")
        with measurement_declaration(), tempfile.TemporaryDirectory() as directory:
            build, _digest, cls.registry, cls.decision = validation.build_measurement_panel(
                ROOT / "metadata" / "sources.json", Path(directory)
            )
            cls.rows = with_reserve_scarcity_state(build.observations)

    def test_a_locked_scored_day_is_refused(self):
        from unittest import mock

        from lockbox_support import PRE_OPENING_LOCKBOX
        from repo_model.splits import LookAheadError

        with mock.patch("repo_model.lockbox.DEFAULT_LOCKBOX", PRE_OPENING_LOCKBOX), self.assertRaisesRegex(LookAheadError, "locked"):
            pm.require_scored_days([date(2025, 12, 31), date(2026, 1, 5)])

    def test_a_day_after_the_last_scored_day_is_refused(self):
        from repo_model.splits import LookAheadError

        with self.assertRaises(LookAheadError):
            pm.require_scored_days([date(2026, 1, 5)])

    def test_an_input_is_read_from_before_the_scored_day(self):
        from dataclasses import replace

        from repo_model.data import DailyObservation
        from repo_model.scarcity import measurement_declaration

        inputs = ("spread_bps", "reserve_balances", "reserve_scarcity_state")
        with measurement_declaration():
            clean = pm.as_of_series(self.rows, self.registry, [r.date for r in self.rows], inputs)
            day = sorted(clean["reserve_balances"])[300]
            marked = []
            for row in self.rows:
                if row.date == day:
                    values = dict(row.values)
                    values["reserve_balances"] = 1e9
                    row = DailyObservation(row.date, values)
                marked.append(row)
            changed = pm.as_of_series(marked, self.registry, [r.date for r in marked], inputs)
        self.assertEqual(changed["reserve_balances"][day], clean["reserve_balances"][day])
        self.assertNotEqual(clean["reserve_balances"][day], 1e9)


class FigureTests(unittest.TestCase):
    def test_a_figure_renders_every_episode_and_is_well_formed(self):
        import xml.dom.minidom

        def path(offset):
            return [
                {"date": f"2020-01-{i + 1:02d}", "probability": 0.02 * i + offset, "cutoff": 0.2, "flag": False, "pressure": False}
                for i in range(11)
            ]

        episodes = [
            {
                "start": "2020-01-11", "regime": "2018-19", "day_type": "ordinary", "missed_by": ["risk_gbm"],
                "path_days": [f"2020-01-{i + 1:02d}" for i in range(11)],
                "models": {n: {"path_h1": path(0.0), "warned_at_lead_at_least_1": n != "risk_gbm"} for n in pm.PASSERS},
            }
        ]
        svg = pm.figure("ordinary", episodes)
        xml.dom.minidom.parseString(svg)
        self.assertEqual(svg.count("<polyline") >= len(pm.PASSERS), True)
        self.assertIn("2020-01-11", svg)


if __name__ == "__main__":
    unittest.main()
