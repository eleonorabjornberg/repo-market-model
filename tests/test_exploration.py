"""The exploratory end date: one constant, the last day of the opened near-blind tier (#684).

`docs/decisions/lockbox.md` (amendment, #151) opened the near-blind tier, 2026-01-01 to 2026-09-03, so it is
ordinary history. Eleonora's instruction on #684 (13 October 2026) moves the exploratory screens' end date from
2025-12-31 to 2026-09-03, in one shared constant, `repo_model.exploration.EXPLORATORY_END`. The blind tier (every
day after 2026-09-03) stays shut.

What is held here:

* the constant is the end of the opened near-blind tier in the tracked declaration, so it cannot drift from it;
* the blind tier is still locked, and `require_exploratory_window` raises `LookAheadError` on a day after the
  constant, and on a day the lockbox itself still locks;
* the three screens (`source_matrix_629`, `derived_features_631`, `off_risk_day_624`) and the screen they follow
  (`source_screen`) read the constant and hold no date of their own.

Recorded mutation (#684), applied in a disposable copy outside the tree: setting `EXPLORATORY_END` in
`src/repo_model/exploration.py` to `date(2026, 9, 4)` makes
`test_the_constant_is_the_end_of_the_opened_near_blind_tier` fail with `AssertionError: datetime.date(2026, 9, 4) !=
datetime.date(2026, 9, 3)` and `test_the_last_day_is_allowed` error with `LookAheadError` (the lockbox still locks the
blind tier's first day). Written first and watched fail (`ModuleNotFoundError: No module named 'repo_model.exploration'`).
A second: in `panel_end`, deleting the `require_exploratory_window([end], where=where)` line makes
`test_an_end_into_the_blind_tier_is_refused` fail with `AssertionError: LookAheadError not raised`.
"""

from __future__ import annotations

import re
import unittest
from datetime import date
from pathlib import Path

from repo_model import exploration
from repo_model.lockbox import load_lockbox
from repo_model.splits import LookAheadError

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
#: `off_risk_day_624` is not here: its step 2 scores through the pressure judge, whose own declaration ends 2025-12-31 (see the PR for #684).
SCREENS = ("source_screen", "source_matrix_629", "derived_features_631")
PANEL_BUILDERS = (
    "pressure_v1_1", "measurement_fields", "net_settlement", "fed_liquidity", "nowcast", "dvp_segment_inputs",
    "early_warning_inputs", "satiation_distance_598",
)


class ExploratoryEndTests(unittest.TestCase):
    def test_the_constant_is_the_end_of_the_opened_near_blind_tier(self):
        opened = [tier for tier in load_lockbox() if tier.opened is not None]
        self.assertTrue(opened, "the near-blind tier is opened in metadata/lockbox.json")
        self.assertEqual(exploration.EXPLORATORY_END, max(tier.end for tier in opened))
        self.assertEqual(exploration.EXPLORATORY_END, date(2026, 9, 3))

    def test_the_blind_tier_is_still_locked(self):
        locked = [tier for tier in load_lockbox() if tier.opened is None]
        self.assertEqual([tier.name for tier in locked], ["blind"])
        self.assertEqual(locked[0].start, date(2026, 9, 4))

    def test_the_last_day_is_allowed(self):
        exploration.require_exploratory_window([date(2025, 12, 31), exploration.EXPLORATORY_END], where="test")

    def test_the_first_blind_day_is_refused(self):
        with self.assertRaises(LookAheadError) as caught:
            exploration.require_exploratory_window([date(2026, 9, 3), date(2026, 9, 4)], where="test")
        self.assertIn("2026-09-04", str(caught.exception))

    def test_a_day_the_lockbox_still_locks_is_refused(self):
        with self.assertRaises(LookAheadError):
            exploration.require_exploratory_window([date(2027, 1, 4)], where="test")


class PanelEndTests(unittest.TestCase):
    """`--end` of the scratch-panel commands: absent, the command keeps its own end; given, it is checked."""

    def test_no_end_keeps_the_commands_own_end(self):
        self.assertEqual(exploration.panel_end(None, date(2025, 12, 31), where="test"), date(2025, 12, 31))

    def test_an_end_inside_the_window_is_taken(self):
        self.assertEqual(exploration.panel_end("2026-09-03", date(2025, 12, 31), where="test"), date(2026, 9, 3))

    def test_an_end_into_the_blind_tier_is_refused(self):
        with self.assertRaises(LookAheadError):
            exploration.panel_end("2026-09-04", date(2025, 12, 31), where="test")

    def test_every_panel_builder_takes_the_end_through_the_guard(self):
        for name in PANEL_BUILDERS:
            with self.subTest(script=name):
                text = (SCRIPTS / f"{name}.py").read_text(encoding="utf-8")
                self.assertIn("panel_end(args.end", text)
                self.assertIn('"--end"', text)


class ScreensReadTheConstantTests(unittest.TestCase):
    def test_no_screen_holds_its_own_end_date(self):
        for name in SCREENS:
            with self.subTest(script=name):
                text = (SCRIPTS / f"{name}.py").read_text(encoding="utf-8")
                self.assertIn("EXPLORATORY_END", text)
                code = "\n".join(line for line in text.splitlines() if not line.lstrip().startswith("#"))
                self.assertIsNone(re.search(r"date\(\s*2025\s*,\s*12\s*,\s*31\s*\)", code))
                self.assertIsNone(re.search(r"^\s*LAST_DAY\s*=\s*[\"']2025", code, re.M))


if __name__ == "__main__":
    unittest.main()
