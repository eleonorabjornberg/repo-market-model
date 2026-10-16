"""The comparison of the cash management bill rule of #738: `scripts/cmb_point_in_time_738.py`.

Pins the figures the finding reported (38 cases, mean absolute error 71.6 against 42.2 bn; 68 `ahead_columns`
cells), that the recorded output is the script's, that no day from the blind tier is read, and that the rule the
comparison calls `after` is the rule `net_settlement.net_for_day` applies.
"""

from __future__ import annotations

import importlib.util
import json
import sys
import unittest
from datetime import date, datetime, time
from pathlib import Path

from repo_model import net_settlement as ns
from repo_model.lockbox import locked_tiers

ROOT = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location("cmb_point_in_time_738", ROOT / "scripts" / "cmb_point_in_time_738.py")
script = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = script
_spec.loader.exec_module(script)


class ComparisonTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = script.build()

    def test_it_reproduces_the_findings_figures(self):
        r = self.result
        self.assertEqual(r["cases_where_a_late_cmb_alone_made_a_class_partial"], 38)
        self.assertEqual(round(r["cmb_cases"]["before"]["mae"], 1), 71.6)
        self.assertEqual(round(r["cmb_cases"]["after"]["mae"], 1), 42.2)
        self.assertEqual(r["ahead_columns"]["cells_changed"], 68)
        self.assertEqual(r["ahead_columns"]["by_year"]["2020"], 43)

    def test_the_cases_are_split_by_every_declared_regime_they_fall_in(self):
        self.assertEqual(sum(t["before"]["n"] for t in self.result["cmb_cases_by_regime"].values()), 38)
        self.assertEqual(sum(t["before"]["n"] for t in self.result["all_cases_by_regime"].values()), self.result["cases"])

    def test_the_recorded_output_is_the_script_output(self):
        recorded = json.loads((script.OUT / "result.json").read_text(encoding="utf-8"))
        self.assertEqual(recorded, json.loads(json.dumps(self.result, sort_keys=True)))
        self.assertEqual((script.OUT / "result.md").read_text(encoding="utf-8"), script.markdown(self.result))

    def test_no_blind_day_is_read(self):
        blind = [t for t in locked_tiers() if t.name == "blind"]
        self.assertTrue(blind)
        self.assertLess(script.LAST_DAY, blind[0].start)

    def test_the_after_reading_is_the_rule_in_force(self):
        declaration = ns.load_declaration(script.audit.DECLARATION)
        auctions = ns.load_snapshot(script.audit.SNAPSHOT, declaration)
        by_day = ns._by_day(auctions)
        checked = 0
        for settles, day in sorted(by_day.items()):
            for announced in sorted({a.announced_at for a in day}):
                instant = datetime.combine(announced.date(), time(12))
                self.assertAlmostEqual(
                    ns.net_for_day(day, instant)[0], script.audit.net(day, instant, "left_out_pit"), places=9
                )
                checked += 1
        self.assertGreater(checked, 1000)


if __name__ == "__main__":
    unittest.main()
